#!/usr/bin/env python3
"""
CHINT Integrated Analytics - ATSE (Automatic Transfer Switch) Deterministic Model Parser
Path: etl/atse_parser.py

Strict, high-performance deterministic grammar parser & validator for ATSE (双电源转换开关电器).
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from etl.base_parser import BaseParseResult, BaseModelParser

# Default Legal Enumerations for ATSE
DEFAULT_ATSE_SERIES: Set[str] = {
    "NXZM", "NXZHM", "NXZHB", "NXZN", "NZ7", "NZ1", "NZ8", "NH40SZ"
}
DEFAULT_ATSE_FRAMES: Set[str] = {
    "63", "80", "100", "125", "160", "225", "250", "320", "400", "630", "800"
}
DEFAULT_ATSE_BREAKINGS: Set[str] = {"S", "H", "F", "标准分断"}
DEFAULT_ATSE_POLES: Set[str] = {"2", "3", "4", "2P", "3P", "4P"}
DEFAULT_ATSE_CONTROLLERS: Set[str] = {"A", "B", "C", "A型", "B型", "C型", "基本型", "智能型"}

ATSE_ACCESSORY_KEYWORDS: List[str] = [
    "外置控制器", "控制器", "连接排", "辅助触点", "备件", "附件", "母排", "安装板", "短路连接条"
]


class ATSEParseResult(BaseParseResult):
    pass


_CACHED_ATSE_CONFIG: Optional[Dict[str, Any]] = None
_SINGLETON_ATSE_PARSER: Optional["ATSEModelParser"] = None


def clear_atse_parser_cache():
    global _CACHED_ATSE_CONFIG, _SINGLETON_ATSE_PARSER
    _CACHED_ATSE_CONFIG = None
    _SINGLETON_ATSE_PARSER = None


def get_atse_parser() -> "ATSEModelParser":
    global _SINGLETON_ATSE_PARSER
    if _SINGLETON_ATSE_PARSER is None:
        _SINGLETON_ATSE_PARSER = ATSEModelParser()
    return _SINGLETON_ATSE_PARSER


class ATSEModelParser(BaseModelParser):
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.legal_series = set(DEFAULT_ATSE_SERIES)
        self.legal_frames = set(DEFAULT_ATSE_FRAMES)
        self.legal_breakings = set(DEFAULT_ATSE_BREAKINGS)
        self.legal_poles = set(DEFAULT_ATSE_POLES)
        self.legal_controllers = set(DEFAULT_ATSE_CONTROLLERS)
        self.accessory_keywords = list(ATSE_ACCESSORY_KEYWORDS)

        if config_override:
            self._apply_config(config_override)
        else:
            self._load_ssot_config()

    def _load_ssot_config(self):
        global _CACHED_ATSE_CONFIG
        if _CACHED_ATSE_CONFIG is not None:
            self._apply_config(_CACHED_ATSE_CONFIG)
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "mapping", "regex", "atse_regex.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    _CACHED_ATSE_CONFIG = cfg
                    self._apply_config(cfg)
            except Exception:
                pass

    def _apply_config(self, cfg: Dict[str, Any]):
        tokens = cfg.get("tokens", {})
        if "models" in tokens and tokens["models"]:
            self.legal_series = set(str(m) for m in tokens["models"]) | self.legal_series
        if "frame_sizes" in tokens and tokens["frame_sizes"]:
            self.legal_frames = set(str(f) for f in tokens["frame_sizes"]) | self.legal_frames
        if "accessory_keywords" in cfg and cfg["accessory_keywords"]:
            self.accessory_keywords = list(set(cfg["accessory_keywords"]) | set(self.accessory_keywords))

    def clean_text_and_extract_current(self, text: str) -> Tuple[str, str, bool]:
        s = str(text or "").strip()
        if not s:
            return "", "未标注", False

        is_accessory = any(kw in s for kw in self.accessory_keywords)
        s = re.sub(r'^特[\s\-_]*', '', s)
        s = s.upper()

        rated_current = "未标注"
        current_match = re.search(r'(?:\s+|-|^)(\d+)\s*A(?:\b|[^\w]|$)', s)
        if current_match:
            rated_current = f"{current_match.group(1)}A"
            s = s[:current_match.start()] + s[current_match.end():]
        else:
            tail_current_match = re.search(r'\s+(\d{1,4})A?$', s)
            if tail_current_match:
                rated_current = f"{tail_current_match.group(1)}A"
                s = s[:tail_current_match.start()]

        s = re.sub(r'\(.*?\)|（.*?）', '', s)
        s = re.sub(r'[\u4e00-\u9fa5]+.*$', '', s)
        s = s.strip()
        return s, rated_current, is_accessory

    def parse(self, text: str) -> ATSEParseResult:
        raw_input = str(text or "").strip()
        if not raw_input:
            return ATSEParseResult(
                raw_input="",
                clean_model="",
                is_valid=False,
                parse_status="解析失败：输入为空",
                data={},
                field_validations={}
            )

        clean_model, rated_current, is_accessory = self.clean_text_and_extract_current(raw_input)

        # Standard ATSE Model Format: {Series}-{Frame}[Breaking]/{Poles}{Controller}[Feature]
        # e.g., NXZM-400S/3A, NXZHM-125/4BT, NXZHB-63/4A, NZ7-63S/3P
        m_atse = re.match(
            r'^([A-Z0-9]+)-(\d{2,4})([SHF])?/(?:(\d)P?([A-Z])([A-Z])?|(\d)P)',
            clean_model
        )
        m_nz7 = re.match(r'^(NZ7|NZ1|NZ8|NH40SZ)-(\d{2,4})([SHF])?/(\d)P', clean_model)

        if is_accessory and not m_atse and not m_nz7:
            extracted_series = ""
            for ser in sorted(self.legal_series, key=len, reverse=True):
                if ser in clean_model:
                    extracted_series = ser
                    break
            return ATSEParseResult(
                raw_input=raw_input,
                clean_model=clean_model,
                is_valid=True,
                parse_status="成功",
                data={
                    "product_model": extracted_series or "未解构型号",
                    "frame_current": "通用壳架",
                    "breaking_capacity": "标准分断",
                    "pole_count": "未指定极数",
                    "controller_type": "未标注",
                    "feature_code": "无",
                    "rated_current": rated_current,
                    "property_type": "附件"
                },
                field_validations={"product_model": "合法" if extracted_series else "未知", "property_type": "合法"}
            )

        if m_atse:
            series = m_atse.group(1)
            frame = m_atse.group(2)
            breaking = m_atse.group(3) or "标准分断"
            
            # Subgroup branch 1: /(\d)P?([A-Z])([A-Z])?
            if m_atse.group(4):
                pole = f"{m_atse.group(4)}P"
                controller = m_atse.group(5) or "A"
                feature = m_atse.group(6) or "无"
            else: # Subgroup branch 2: /(\d)P
                pole = f"{m_atse.group(7)}P"
                controller = "A"
                feature = "无"

            data = {
                "product_model": series,
                "frame_current": frame,
                "breaking_capacity": breaking,
                "pole_count": pole,
                "controller_type": controller,
                "feature_code": feature,
                "rated_current": rated_current,
                "property_type": "本体"
            }
            validations, is_valid, global_status = self._validate_atse_fields(data)
            return ATSEParseResult(raw_input=raw_input, clean_model=clean_model, is_valid=is_valid, parse_status=global_status, data=data, field_validations=validations)

        # Legacy NZ7 Hyphenated: NZ7-63S/3P-63A
        m_nz7 = re.match(r'^(NZ7|NZ1|NZ8|NH40SZ)-(\d{2,4})([SHF])?/(\d)P', clean_model)
        if m_nz7:
            series = m_nz7.group(1)
            frame = m_nz7.group(2)
            breaking = m_nz7.group(3) or "S"
            pole = f"{m_nz7.group(4)}P"
            data = {
                "product_model": series,
                "frame_current": frame,
                "breaking_capacity": breaking,
                "pole_count": pole,
                "controller_type": "A",
                "feature_code": "无",
                "rated_current": rated_current,
                "property_type": "本体"
            }
            validations, is_valid, global_status = self._validate_atse_fields(data)
            return ATSEParseResult(raw_input=raw_input, clean_model=clean_model, is_valid=is_valid, parse_status=global_status, data=data, field_validations=validations)

        # Fallback check series
        series_m = re.match(r'^([A-Za-z0-9]+?)(?:\d|\-)', clean_model)
        unknown_series = series_m.group(1) if series_m else "未知"

        return ATSEParseResult(
            raw_input=raw_input,
            clean_model=clean_model,
            is_valid=False,
            parse_status=f"异常：未知系列 [{unknown_series}]" if unknown_series not in self.legal_series else "解析失败：型号格式不匹配",
            data={"product_model": unknown_series, "property_type": "待确认"},
            field_validations={"product_model": "未知系列", "format": "格式不匹配"}
        )

    def _validate_atse_fields(self, data: Dict[str, str]) -> Tuple[Dict[str, str], bool, str]:
        validations: Dict[str, str] = {}
        issues: List[str] = []

        series = data.get("product_model", "")
        if series in self.legal_series:
            validations["product_model"] = "合法"
        else:
            validations["product_model"] = "未知系列"
            issues.append(f"未知系列 [{series}]")

        frame = data.get("frame_current", "")
        if frame in self.legal_frames:
            validations["frame_current"] = "合法"
        else:
            validations["frame_current"] = "未知壳架"
            issues.append(f"未知壳架 [{frame}]")

        breaking = data.get("breaking_capacity", "")
        validations["breaking_capacity"] = "合法" if (breaking in self.legal_breakings or breaking == "标准分断") else "未知分断"

        pole = data.get("pole_count", "")
        validations["pole_count"] = "合法" if pole in self.legal_poles else "极数异常"

        controller = data.get("controller_type", "")
        validations["controller_type"] = "合法" if controller in self.legal_controllers else "未知控制器级别"

        validations["feature_code"] = "合法"
        validations["rated_current"] = "合法" if data.get("rated_current") != "未标注" else "未标注"
        validations["property_type"] = "合法"

        is_valid = len(issues) == 0
        global_status = "成功" if is_valid else "异常：" + "，".join(issues)
        return validations, is_valid, global_status
