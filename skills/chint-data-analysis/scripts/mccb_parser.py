#!/usr/bin/env python3
"""
CHINT Integrated Analytics - MCCB Deterministic Model Parser & Decomposition Engine
Path: etl/mccb_parser.py

Strict, high-performance deterministic grammar state-machine & validator for Low-Voltage
Molded Case Circuit Breakers (MCCB / 塑壳断路器).
Implements zero silent failure, fine-grained field status tracking, and high-throughput batch processing.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from etl.base_parser import BaseParseResult, BaseModelParser


# Standard Default Legal Enums for MCCB
DEFAULT_LEGAL_SERIES: Set[str] = {
    "NXM", "NXMS", "NXMNS", "NXMSH", "NXMSP", "NXMSPD", "NXMLE", "NXMP", "NXMH", "NXMN",
    "NXMNLE", "NXMHLE", "NXMPLE", "NXHM", "NXMF",
    "DZ15", "DZ15LE", "DZ20", "DZ20L", "DZ20Y", "NL18",
    "NM1", "NM10", "NM1B", "NM1e", "NM1LE", "NM2", "NM2FC", "NM2LC",
    "NM5", "NM5NE", "NM5LE", "NM5S", "NM5NELE", "NM5P", "NM5NEDC",
    "NM8N", "NM8NL", "NM8NDC", "NM3", "NM3N", "NM5PLE", "NXA", "Ex9M", "Ex9MD", "Ex9MY", "Ex9M1", "Ex9M2"
}

DEFAULT_LEGAL_FRAMES: Set[str] = {
    "40", "63", "100", "125", "160", "225", "250", "320", "400", "500", "630", "800",
    "1000", "1250", "1600", "W125", "W630", "W800"
}

DEFAULT_LEGAL_BREAKINGS: Set[str] = {"S", "H", "F", "Q", "R", "U", "N", "M", "C", "ST"}
DEFAULT_LEGAL_POLES: Set[str] = {"2", "3", "4", "2P", "3P", "4P"}
DEFAULT_LEGAL_N_POLES: Set[str] = {"A", "B", "C", "D", "无"}
DEFAULT_LEGAL_OPERATIONS: Set[str] = {"P", "Z", "手动", "电动", "转动", "手柄", "标准操作"}

DEFAULT_ACCESSORY_KEYWORDS: List[str] = [
    "分励脱扣器", "欠压脱扣器", "辅助触头", "报警触头", "电动操作机构",
    "转动手柄", "相间隔板", "加长手柄", "抽屉架", "零部件", "备件", "底座", "接线板", "门框"
]


_CACHED_SSOT_CONFIG: Optional[Dict[str, Any]] = None
_SINGLETON_PARSER: Optional["MCCBModelParser"] = None


def clear_mccb_parser_cache():
    """Clears global cached SSOT config and singleton parser instance."""
    global _CACHED_SSOT_CONFIG, _SINGLETON_PARSER
    _CACHED_SSOT_CONFIG = None
    _SINGLETON_PARSER = None


def get_mccb_parser(config_override: Optional[Dict[str, Any]] = None) -> "MCCBModelParser":
    """Returns singleton MCCB parser instance or creates new with override."""
    global _SINGLETON_PARSER
    if config_override is not None:
        return MCCBModelParser(config_override)
    if _SINGLETON_PARSER is None:
        _SINGLETON_PARSER = MCCBModelParser()
    return _SINGLETON_PARSER


class MCCBParseResult(BaseParseResult):
    pass


class MCCBModelParser(BaseModelParser):
    """
    Deterministic 2-Stage MCCB Model Parser:
    Stage 1: Noise cleaning & Rated Current isolation.
    Stage 2: Strict grammar segmentation (Slashed vs Compact) + Legal Enum Validation.
    """

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.legal_series = set(DEFAULT_LEGAL_SERIES)
        self.legal_frames = set(DEFAULT_LEGAL_FRAMES)
        self.legal_breakings = set(DEFAULT_LEGAL_BREAKINGS)
        self.legal_poles = set(DEFAULT_LEGAL_POLES)
        self.legal_n_poles = set(DEFAULT_LEGAL_N_POLES)
        self.legal_operations = set(DEFAULT_LEGAL_OPERATIONS)
        self.accessory_keywords = list(DEFAULT_ACCESSORY_KEYWORDS)

        if config_override:
            self._apply_config(config_override)
        else:
            self._load_ssot_config()

    def _load_ssot_config(self):
        """Loads departmental regex JSON configuration with in-memory caching."""
        global _CACHED_SSOT_CONFIG
        if _CACHED_SSOT_CONFIG is not None:
            self._apply_config(_CACHED_SSOT_CONFIG)
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "mapping", "regex", "mccb_regex.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    _CACHED_SSOT_CONFIG = cfg
                    self._apply_config(cfg)
            except Exception as e:
                print(f"[MCCB Parser] Warning reading {json_path}: {e}")

    def _apply_config(self, cfg: Dict[str, Any]):
        """Merges tokens and accessory keywords from configuration dictionary."""
        tokens = cfg.get("tokens", {})
        if "models" in tokens and tokens["models"]:
            self.legal_series = set(str(m) for m in tokens["models"]) | self.legal_series
        if "frame_sizes" in tokens and tokens["frame_sizes"]:
            self.legal_frames = set(str(f) for f in tokens["frame_sizes"]) | self.legal_frames
        if "breaking_capacities" in tokens and tokens["breaking_capacities"]:
            self.legal_breakings = set(str(b) for b in tokens["breaking_capacities"]) | self.legal_breakings
        if "operation_methods" in tokens and tokens["operation_methods"]:
            self.legal_operations = set(str(o) for o in tokens["operation_methods"]) | self.legal_operations
        if "accessory_keywords" in cfg and cfg["accessory_keywords"]:
            self.accessory_keywords = list(set(cfg["accessory_keywords"]) | set(self.accessory_keywords))

    def clean_text_and_extract_current(self, text: str) -> Tuple[str, str, bool]:
        """
        Step 1 & Step 2: Clean input string and extract rated current.
        Returns: (cleaned_model_str, rated_current_str, is_explicit_accessory)
        """
        s = str(text or "").strip()
        if not s:
            return "", "未标注", False

        # Detect accessory keywords before heavy cleaning
        is_accessory = any(kw in s for kw in self.accessory_keywords)

        # Remove leading "特 " or "特"
        s = re.sub(r'^特[\s\-_]*', '', s)

        # Standardize uppercase for Latin characters
        s = s.upper()

        # Extract rated current: space + digits + 'A' (e.g. " 63A", " 40A(R)", " 160A AC230V")
        rated_current = "未标注"
        current_match = re.search(r'(?:\s+|^)(\d+)\s*A(?:\b|[^\w]|$)', s)
        if current_match:
            rated_current = f"{current_match.group(1)}A"
            # Remove current part and trailing suffix noise from main model code
            s = s[:current_match.start()] + s[current_match.end():]
        else:
            # Check standalone current like " 630A" at the end of string
            tail_current_match = re.search(r'\s+(\d{1,4})A?$', s)
            if tail_current_match:
                rated_current = f"{tail_current_match.group(1)}A"
                s = s[:tail_current_match.start()]

        # Clean noise suffixes: electrical specs (AC230V, DC24V, 50Hz, 100mA, etc.), remarks in brackets
        s = re.sub(r'\(.*?\)|（.*?）', '', s)
        s = re.sub(r'\b(?:AC|DC)\s*\d+V\b', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\b\d+\s*(?:HZ|MA|V)\b', '', s, flags=re.IGNORECASE)
        s = re.sub(r'[\u4e00-\u9fa5]+.*$', '', s) # Strip trailing Chinese remarks
        s = re.sub(r'\s+[A-Z0-9]$', '', s) # Strip trailing single letter noise like ' G', ' C'
        s = s.strip()

        return s, rated_current, is_accessory

    def parse(self, text: str) -> MCCBParseResult:
        """
        Executes strict 7-step parsing and validation for a single model string.
        """
        raw_input = str(text or "").strip()
        if not raw_input:
            return MCCBParseResult(
                raw_input="",
                clean_model="",
                is_valid=False,
                parse_status="解析失败：输入为空",
                data={},
                field_validations={}
            )

        clean_model, rated_current, is_accessory = self.clean_text_and_extract_current(raw_input)

        # Check for absolute format mismatch (must contain '-' or recognized series)
        has_hyphen = '-' in clean_model
        if not has_hyphen:
            # Check if an accessory
            if is_accessory:
                # Attempt partial model extraction
                extracted_series = ""
                for ser in sorted(self.legal_series, key=len, reverse=True):
                    if ser in clean_model:
                        extracted_series = ser
                        break
                return MCCBParseResult(
                    raw_input=raw_input,
                    clean_model=clean_model,
                    is_valid=True,
                    parse_status="成功",
                    data={
                        "product_model": extracted_series or "未解构型号",
                        "frame_current": "通用壳架",
                        "breaking_capacity": "标准分断",
                        "pole_count": "未指定极数",
                        "n_pole_type": "无",
                        "operation_method": "标准操作",
                        "accessory_code": "未标注",
                        "rated_current": rated_current,
                        "property_type": "附件"
                    },
                    field_validations={
                        "product_model": "合法" if extracted_series else "未知",
                        "property_type": "合法",
                        "rated_current": "合法" if rated_current != "未标注" else "未标注"
                    }
                )

            return MCCBParseResult(
                raw_input=raw_input,
                clean_model=clean_model,
                is_valid=False,
                parse_status="解析失败：型号格式不匹配",
                data={"property_type": "待确认"},
                field_validations={"format": "格式不匹配"}
            )

        # Determine parsing branch: Standard Slashed vs Compact
        if '/' in clean_model:
            parsed_data, status_msg = self._parse_slashed_format(clean_model)
        else:
            parsed_data, status_msg = self._parse_compact_format(clean_model)

        parsed_data["rated_current"] = rated_current

        # Validate against legal enums
        validations, is_valid, global_status = self._validate_and_evaluate(parsed_data, is_accessory)
        if status_msg and "异常" in status_msg:
            global_status = status_msg
            is_valid = False

        return MCCBParseResult(
            raw_input=raw_input,
            clean_model=clean_model,
            is_valid=is_valid,
            parse_status=global_status,
            data=parsed_data,
            field_validations=validations
        )

    def _parse_slashed_format(self, model_str: str) -> Tuple[Dict[str, str], str]:
        """
        Parses standard format: {Series}-{Frame}[Op]{Breaking}/{Poles}{AccessoryCode}{NPole}
        e.g. NXMS-160H/4300C or NM1-63SZ/3300
        """
        parts = model_str.split('/', 1)
        head = parts[0].strip()
        tail = parts[1].strip() if len(parts) > 1 else ""

        data: Dict[str, str] = {
            "product_model": "",
            "frame_current": "",
            "breaking_capacity": "",
            "operation_method": "标准操作",
            "pole_count": "",
            "accessory_code": "未标注",
            "n_pole_type": "无",
            "property_type": "本体"
        }
        status_msg = ""

        # 1. Parse Head: Split by '-'
        head_parts = head.split('-', 1)
        series_part = head_parts[0].strip()
        data["product_model"] = series_part

        spec_part = head_parts[1].strip() if len(head_parts) > 1 else ""
        if spec_part:
            # Spec part breakdown: Frame size + [Operation] + Breaking Capacity
            # e.g., "160H", "W125S", "63SZ", "250HP"
            # Extract Frame (starts with optional W, followed by digits)
            frame_m = re.match(r'^(W?\d+)', spec_part)
            if frame_m:
                data["frame_current"] = frame_m.group(1)
                rem = spec_part[len(data["frame_current"]):]
                
                # Check breaking capacity and operation
                # Possible patterns in rem: "H", "S", "SZ", "HP", "SP", "ST", "P", "Z"
                if rem in ("P", "Z"):
                    data["operation_method"] = rem
                    data["breaking_capacity"] = "标准分断"
                elif rem in ("SZ", "HZ", "FZ", "SP", "HP", "FP"):
                    data["breaking_capacity"] = rem[0]
                    data["operation_method"] = rem[1]
                elif len(rem) >= 1:
                    data["breaking_capacity"] = rem
                else:
                    data["breaking_capacity"] = "标准分断"
            else:
                data["frame_current"] = spec_part

        # 2. Parse Tail: {Poles}{AccessoryCode}{NPole}
        # e.g. "4300C", "3320", "3300", "4300B"
        if tail:
            tail_clean = tail
            # Check N-Pole letter at end
            if tail_clean[-1] in ('A', 'B', 'C', 'D'):
                data["n_pole_type"] = tail_clean[-1]
                tail_clean = tail_clean[:-1]
            else:
                data["n_pole_type"] = "无"

            if len(tail_clean) >= 1:
                p_char = tail_clean[0]
                data["pole_count"] = f"{p_char}P"
                
                # Accessory code is the remaining 3 or more digits (e.g. 300, 320, 200)
                if len(tail_clean) >= 4:
                    data["accessory_code"] = tail_clean[1:4]
                elif len(tail_clean) > 1:
                    data["accessory_code"] = tail_clean[1:]
            else:
                data["pole_count"] = "未指定极数"

        return data, status_msg

    def _parse_compact_format(self, model_str: str) -> Tuple[Dict[str, str], str]:
        """
        Parses compact format without slash: {Series}-{Frame}{Breaking}{Op}{Poles}{Accessory}{NPole}
        e.g. NXM-W125SP4300A
        """
        data: Dict[str, str] = {
            "product_model": "",
            "frame_current": "",
            "breaking_capacity": "",
            "operation_method": "标准操作",
            "pole_count": "",
            "accessory_code": "未标注",
            "n_pole_type": "无",
            "property_type": "本体"
        }
        status_msg = ""

        parts = model_str.split('-', 1)
        data["product_model"] = parts[0].strip()
        rem = parts[1].strip() if len(parts) > 1 else ""

        if rem:
            # 1. Match Frame (longest matching legal frame or W?\d+)
            frame_m = re.match(r'^(W?\d+)', rem)
            if frame_m:
                data["frame_current"] = frame_m.group(1)
                rem = rem[len(data["frame_current"]):]

            # 2. Match Breaking capacity
            if rem and rem[0] in ('S', 'H', 'F', 'Q', 'R', 'U', 'N', 'M', 'C'):
                data["breaking_capacity"] = rem[0]
                rem = rem[1:]

            # 3. Match Operation method
            if rem and rem[0] in ('P', 'Z'):
                data["operation_method"] = rem[0]
                rem = rem[1:]

            # 4. Match N-pole at end if any
            if rem and rem[-1] in ('A', 'B', 'C', 'D'):
                data["n_pole_type"] = rem[-1]
                rem = rem[:-1]

            # 5. Match Poles & Accessory Code
            if rem and rem[0] in ('2', '3', '4'):
                data["pole_count"] = f"{rem[0]}P"
                if len(rem) >= 4:
                    data["accessory_code"] = rem[1:4]
                elif len(rem) > 1:
                    data["accessory_code"] = rem[1:]

        return data, status_msg

    def _validate_and_evaluate(self, data: Dict[str, str], is_explicit_accessory: bool) -> Tuple[Dict[str, str], bool, str]:
        """
        Validates parsed fields against the legal enumeration library and generates
        field-level status and global parse status.
        """
        validations: Dict[str, str] = {}
        issues: List[str] = []

        # 1. Series validation
        series = data.get("product_model", "")
        if not series:
            validations["product_model"] = "未标注"
            issues.append("缺失系列")
        elif series in self.legal_series:
            validations["product_model"] = "合法"
        else:
            validations["product_model"] = "未知系列"
            issues.append(f"未知系列 [{series}]")

        # 2. Frame Size validation
        frame = data.get("frame_current", "")
        if not frame or frame == "通用壳架":
            validations["frame_current"] = "未标注"
        elif frame in self.legal_frames:
            validations["frame_current"] = "合法"
        else:
            validations["frame_current"] = "未知壳架代号"
            issues.append(f"未知壳架 [{frame}]")

        # 3. Breaking capacity validation
        breaking = data.get("breaking_capacity", "")
        if not breaking or breaking == "标准分断":
            validations["breaking_capacity"] = "默认值"
        elif breaking in self.legal_breakings:
            validations["breaking_capacity"] = "合法"
        else:
            validations["breaking_capacity"] = "未知分断等级"
            issues.append(f"未知分断 [{breaking}]")

        # 4. Pole count validation
        pole = data.get("pole_count", "")
        clean_pole = pole.rstrip('P') if pole else ""
        if not pole or pole == "未指定极数":
            validations["pole_count"] = "未标注"
        elif clean_pole in ('2', '3', '4'):
            validations["pole_count"] = "合法"
        else:
            validations["pole_count"] = "极数异常"
            issues.append(f"极数异常 [{pole}]")

        # 5. Accessory code validation
        acc_code = data.get("accessory_code", "")
        if not acc_code or acc_code == "未标注":
            validations["accessory_code"] = "未标注"
        elif len(acc_code) == 3 and acc_code.isdigit():
            validations["accessory_code"] = "合法"
        else:
            validations["accessory_code"] = "非标附件码"

        # 6. N-Pole type validation
        n_pole = data.get("n_pole_type", "无")
        if n_pole in self.legal_n_poles:
            validations["n_pole_type"] = "合法"
        else:
            validations["n_pole_type"] = "未知N极方式"
            issues.append(f"未知N极 [{n_pole}]")

        # 7. Operation method validation
        op = data.get("operation_method", "标准操作")
        if op in self.legal_operations:
            validations["operation_method"] = "合法" if op != "标准操作" else "默认值"
        else:
            validations["operation_method"] = "未知操作方式"

        # 8. Rated current validation
        current = data.get("rated_current", "未标注")
        validations["rated_current"] = "合法" if current != "未标注" else "未标注"

        # 9. Property classification (本体 vs 附件)
        has_complete_body = (
            validations.get("product_model") == "合法" and 
            validations.get("frame_current") == "合法" and 
            validations.get("pole_count") == "合法"
        )

        if has_complete_body:
            # Complete breaker body code takes precedence (e.g. NXM-125S/3300 带电动操作机构 is 本体)
            data["property_type"] = "本体"
            validations["property_type"] = "合法"
        elif is_explicit_accessory:
            # Standalone accessory / incomplete breaker code
            data["property_type"] = "附件"
            validations["property_type"] = "合法"
        elif validations.get("product_model") == "合法" and validations.get("frame_current") == "合法":
            data["property_type"] = "本体"
            validations["property_type"] = "合法"
        else:
            data["property_type"] = "待确认"
            validations["property_type"] = "待人工确认"

        # Determine overall status
        if not issues:
            global_status = "成功"
            is_valid = True
        else:
            global_status = "异常：" + "，".join(issues)
            is_valid = False

        return validations, is_valid, global_status

