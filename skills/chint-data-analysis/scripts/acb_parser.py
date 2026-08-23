#!/usr/bin/env python3
"""
CHINT Integrated Analytics - ACB (Air Circuit Breaker) Deterministic Model Parser
Path: etl/acb_parser.py

Strict, high-performance deterministic grammar parser & validator for Air Circuit Breakers (ACB / 框架断路器).
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from etl.base_parser import BaseParseResult, BaseModelParser

# Default Legal Enumerations for ACB
DEFAULT_ACB_SERIES: Set[str] = {"NXA", "NA1", "DW15", "DW17", "Ex9A", "NXA1"}
DEFAULT_ACB_FRAMES: Set[str] = {"16", "20", "25", "32", "40", "50", "63", "1600", "2000", "2500", "3200", "4000", "6300"}
DEFAULT_ACB_BREAKINGS: Set[str] = {"N", "H", "S", "标准型", "较高型"}
DEFAULT_ACB_CONTROLLERS: Set[str] = {"M", "A", "P", "H", "3H", "2H", "基本型", "电流型", "功率型", "谐波型"}
DEFAULT_ACB_INSTALLATIONS: Set[str] = {"D", "F", "抽屉式", "固定式"}
DEFAULT_ACB_POLES: Set[str] = {"3", "4", "3P", "4P"}

ACB_CURRENT_CODE_MAP: Dict[str, str] = {
    "04": "400A", "06": "630A", "08": "800A", "10": "1000A", "12": "1250A",
    "16": "1600A", "20": "2000A", "25": "2500A", "29": "2900A", "32": "3200A",
    "36": "3600A", "40": "4000A", "50": "5000A", "63": "6300A"
}

ACB_ACCESSORY_KEYWORDS: List[str] = [
    "抽屉座", "抽屉架", "二次接插件", "分励脱扣器", "闭合电磁铁", "欠电压脱扣器",
    "电动操作机构", "辅助触头", "门框", "接地附件", "机械联锁", "控制器", "备件", "服务"
]


class ACBParseResult(BaseParseResult):
    pass


_CACHED_ACB_CONFIG: Optional[Dict[str, Any]] = None
_SINGLETON_ACB_PARSER: Optional["ACBModelParser"] = None


def clear_acb_parser_cache():
    global _CACHED_ACB_CONFIG, _SINGLETON_ACB_PARSER
    _CACHED_ACB_CONFIG = None
    _SINGLETON_ACB_PARSER = None


def get_acb_parser() -> "ACBModelParser":
    global _SINGLETON_ACB_PARSER
    if _SINGLETON_ACB_PARSER is None:
        _SINGLETON_ACB_PARSER = ACBModelParser()
    return _SINGLETON_ACB_PARSER


class ACBModelParser(BaseModelParser):
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.legal_series = set(DEFAULT_ACB_SERIES)
        self.legal_frames = set(DEFAULT_ACB_FRAMES)
        self.legal_breakings = set(DEFAULT_ACB_BREAKINGS)
        self.legal_controllers = set(DEFAULT_ACB_CONTROLLERS)
        self.legal_installations = set(DEFAULT_ACB_INSTALLATIONS)
        self.legal_poles = set(DEFAULT_ACB_POLES)
        self.accessory_keywords = list(ACB_ACCESSORY_KEYWORDS)

        if config_override:
            self._apply_config(config_override)
        else:
            self._load_ssot_config()

    def _load_ssot_config(self):
        global _CACHED_ACB_CONFIG
        if _CACHED_ACB_CONFIG is not None:
            self._apply_config(_CACHED_ACB_CONFIG)
            return

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, "data", "mapping", "regex", "acb_regex.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    _CACHED_ACB_CONFIG = cfg
                    self._apply_config(cfg)
            except Exception:
                pass

    def _apply_config(self, cfg: Dict[str, Any]):
        tokens = cfg.get("tokens", {})
        if "models" in tokens and tokens["models"]:
            self.legal_series = set(str(m) for m in tokens["models"]) | self.legal_series
        if "frame_sizes" in tokens and tokens["frame_sizes"]:
            self.legal_frames = set(str(f) for f in tokens["frame_sizes"]) | self.legal_frames
        if "breaking_capacities" in tokens and tokens["breaking_capacities"]:
            self.legal_breakings = set(str(b) for b in tokens["breaking_capacities"]) | self.legal_breakings
        if "accessory_keywords" in cfg and cfg["accessory_keywords"]:
            self.accessory_keywords = list(set(cfg["accessory_keywords"]) | set(self.accessory_keywords))

    def clean_text(self, text: str) -> Tuple[str, bool]:
        s = str(text or "").strip()
        is_accessory = any(kw in s for kw in self.accessory_keywords)
        s = re.sub(r'^特[\s\-_]*', '', s)
        s = s.upper()
        return s, is_accessory

    def parse(self, text: str) -> ACBParseResult:
        raw_input = str(text or "").strip()
        if not raw_input:
            return ACBParseResult(
                raw_input="",
                clean_model="",
                is_valid=False,
                parse_status="解析失败：输入为空",
                data={},
                field_validations={}
            )

        clean_model, is_accessory = self.clean_text(raw_input)

        if is_accessory and not re.search(r'\bNXA\d{2}[A-Z]\d{2}', clean_model):
            # Accessory branch
            extracted_series = ""
            for ser in sorted(self.legal_series, key=len, reverse=True):
                if ser in clean_model:
                    extracted_series = ser
                    break
            return ACBParseResult(
                raw_input=raw_input,
                clean_model=clean_model,
                is_valid=True,
                parse_status="成功",
                data={
                    "product_model": extracted_series or "未解构型号",
                    "frame_current": "通用壳架",
                    "breaking_capacity": "标准分断",
                    "rated_current": "未标注",
                    "controller_type": "未标注",
                    "installation_type": "未标注",
                    "pole_count": "未指定极数",
                    "control_voltage": "未标注",
                    "property_type": "附件"
                },
                field_validations={"product_model": "合法" if extracted_series else "未知", "property_type": "合法"}
            )

        # 1. Try Compact Modern NXA Format: NXA16H06-MD3-AC220/230/240
        m_compact = re.match(
            r'^(NXA|NA1|DW15|DW17|Ex9A|NXA1)(\d{2})([A-Z])(\d{2})(?:-([A-Z0-9]+))?(?:-([A-Z0-9/]+))?(?:-([A-Z0-9]+))?$',
            clean_model
        )

        if m_compact:
            series = m_compact.group(1)
            frame_code = m_compact.group(2)
            breaking_code = m_compact.group(3)
            current_code = m_compact.group(4)
            spec_mid = m_compact.group(5) or ""
            voltage_part = m_compact.group(6) or "未标注"

            # Parse mid spec: e.g. "MD3", "MF3", "MD4", "3H-D-3"
            controller = "M"
            installation = "D"
            pole = "3P"

            if len(spec_mid) >= 3:
                controller = spec_mid[0]
                installation = spec_mid[1]
                pole_char = spec_mid[2]
                pole = f"{pole_char}P" if pole_char in ('3', '4') else pole_char
            elif len(spec_mid) == 2:
                installation = spec_mid[0]
                pole_char = spec_mid[1]
                pole = f"{pole_char}P" if pole_char in ('3', '4') else pole_char

            rated_current_str = ACB_CURRENT_CODE_MAP.get(current_code, f"{current_code}00A" if int(current_code) >= 4 else f"{current_code}A")

            data = {
                "product_model": series,
                "frame_current": frame_code,
                "breaking_capacity": breaking_code,
                "rated_current": rated_current_str,
                "controller_type": controller,
                "installation_type": installation,
                "pole_count": pole,
                "control_voltage": voltage_part,
                "property_type": "本体"
            }
            validations, is_valid, global_status = self._validate_acb_fields(data)
            return ACBParseResult(raw_input=raw_input, clean_model=clean_model, is_valid=is_valid, parse_status=global_status, data=data, field_validations=validations)

        # 2. Try Hyphenated Format: NXA-16N-04-M-D-3-AC230-M
        m_hyphen = re.match(
            r'^(NXA|NA1|DW15|DW17|Ex9A|NXA1)-(\d{2,4})([A-Z])?-(\d{2,4})-([A-Z0-9]+)-([DF])-([34])(?:-([A-Z0-9/]+))?(?:-([A-Z0-9]+))?$',
            clean_model
        )
        if m_hyphen:
            series = m_hyphen.group(1)
            frame_code = m_hyphen.group(2)
            breaking_code = m_hyphen.group(3) or "N"
            current_code = m_hyphen.group(4)
            controller = m_hyphen.group(5)
            installation = m_hyphen.group(6)
            pole = f"{m_hyphen.group(7)}P"
            voltage_part = m_hyphen.group(8) or "未标注"

            rated_current_str = ACB_CURRENT_CODE_MAP.get(current_code, f"{current_code}A")
            data = {
                "product_model": series,
                "frame_current": frame_code,
                "breaking_capacity": breaking_code,
                "rated_current": rated_current_str,
                "controller_type": controller,
                "installation_type": installation,
                "pole_count": pole,
                "control_voltage": voltage_part,
                "property_type": "本体"
            }
            validations, is_valid, global_status = self._validate_acb_fields(data)
            return ACBParseResult(raw_input=raw_input, clean_model=clean_model, is_valid=is_valid, parse_status=global_status, data=data, field_validations=validations)

        # 3. Try Legacy NA1 Format: NA1-2000-1600M/3
        m_na1 = re.match(r'^(NA1|DW15|DW17)-(\d{3,4})-(\d{3,4})([A-Z])?/([34])(?:\s*.*)?$', clean_model)
        if m_na1:
            series = m_na1.group(1)
            frame_code = m_na1.group(2)
            current_code = m_na1.group(3)
            controller = m_na1.group(4) or "M"
            pole = f"{m_na1.group(5)}P"
            data = {
                "product_model": series,
                "frame_current": frame_code,
                "breaking_capacity": "标准分断",
                "rated_current": f"{current_code}A",
                "controller_type": controller,
                "installation_type": "D",
                "pole_count": pole,
                "control_voltage": "未标注",
                "property_type": "本体"
            }
            validations, is_valid, global_status = self._validate_acb_fields(data)
            return ACBParseResult(raw_input=raw_input, clean_model=clean_model, is_valid=is_valid, parse_status=global_status, data=data, field_validations=validations)

        # Failed match
        # Check if first part matches an unknown series
        series_m = re.match(r'^([A-Za-z0-9]+?)(?:\d|\-)', clean_model)
        unknown_series = series_m.group(1) if series_m else "未知"

        return ACBParseResult(
            raw_input=raw_input,
            clean_model=clean_model,
            is_valid=False,
            parse_status=f"异常：未知系列 [{unknown_series}]" if unknown_series not in self.legal_series else "解析失败：型号格式不匹配",
            data={"product_model": unknown_series, "property_type": "待确认"},
            field_validations={"product_model": "未知系列", "format": "格式不匹配"}
        )

    def _validate_acb_fields(self, data: Dict[str, str]) -> Tuple[Dict[str, str], bool, str]:
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

        current = data.get("rated_current", "")
        validations["rated_current"] = "合法" if current != "未标注" else "未标注"

        controller = data.get("controller_type", "")
        validations["controller_type"] = "合法" if controller in self.legal_controllers else "未知控制器"

        installation = data.get("installation_type", "")
        validations["installation_type"] = "合法" if installation in self.legal_installations else "未知安装方式"

        pole = data.get("pole_count", "")
        validations["pole_count"] = "合法" if pole in self.legal_poles else "极数异常"

        validations["control_voltage"] = "合法" if data.get("control_voltage") != "未标注" else "未标注"
        validations["property_type"] = "合法"

        is_valid = len(issues) == 0
        global_status = "成功" if is_valid else "异常：" + "，".join(issues)
        return validations, is_valid, global_status
