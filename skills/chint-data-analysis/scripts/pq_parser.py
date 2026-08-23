#!/usr/bin/env python3
"""
CHINT Integrated Analytics - PQ (Power Quality) Deterministic Model Parser
Path: etl/pq_parser.py

Strict, high-performance deterministic grammar parser for Power Quality products (APF, SVG, Capacitors).
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from etl.base_parser import BaseParseResult, BaseModelParser

DEFAULT_PQ_SERIES: Set[str] = {"APF", "SVG", "NJK", "CJ19", "ANAPF", "ANSVG"}
PQ_ACCESSORY_KEYWORDS: List[str] = ["采样互感器", "CT", "电抗器", "控制器", "通信模块", "备件", "附件"]


class PQParseResult(BaseParseResult):
    pass


_SINGLETON_PQ_PARSER: Optional["PQModelParser"] = None


def clear_pq_parser_cache():
    global _SINGLETON_PQ_PARSER
    _SINGLETON_PQ_PARSER = None


def get_pq_parser() -> "PQModelParser":
    global _SINGLETON_PQ_PARSER
    if _SINGLETON_PQ_PARSER is None:
        _SINGLETON_PQ_PARSER = PQModelParser()
    return _SINGLETON_PQ_PARSER


class PQModelParser(BaseModelParser):
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        self.legal_series = set(DEFAULT_PQ_SERIES)
        self.accessory_keywords = list(PQ_ACCESSORY_KEYWORDS)

    def parse(self, text: str) -> PQParseResult:
        raw_input = str(text or "").strip()
        if not raw_input:
            return PQParseResult(raw_input="", clean_model="", is_valid=False, parse_status="解析失败：输入为空", data={}, field_validations={})

        s = re.sub(r'^特[\s\-_]*', '', raw_input).upper().strip()
        is_accessory = any(kw in raw_input for kw in self.accessory_keywords)

        if is_accessory:
            return PQParseResult(
                raw_input=raw_input, clean_model=s, is_valid=True, parse_status="成功",
                data={"product_model": "PQ附件", "capacity_rating": "未标注", "voltage_rating": "未标注", "installation_type": "未标注", "property_type": "附件"},
                field_validations={"property_type": "合法"}
            )

        # 1. Active Filters & SVG: APF-100A/400V-F or SVG-200kvar/400V-R
        m_apf_svg = re.match(r'^(APF|SVG|ANAPF|ANSVG)-(\d+)(?:A|KVAR|kvar)?/(\d+V)?-?([A-Z])?', s, re.IGNORECASE)
        if m_apf_svg:
            series = m_apf_svg.group(1).upper()
            cap_num = m_apf_svg.group(2)
            volt = m_apf_svg.group(3) or "400V"
            inst = m_apf_svg.group(4) or "F"
            cap_str = f"{cap_num}A" if series in ("APF", "ANAPF") else f"{cap_num}kvar"

            data = {
                "product_model": series,
                "capacity_rating": cap_str,
                "voltage_rating": volt.upper(),
                "installation_type": inst.upper(),
                "property_type": "本体"
            }
            return PQParseResult(
                raw_input=raw_input, clean_model=s, is_valid=True, parse_status="成功",
                data=data,
                field_validations={"product_model": "合法", "capacity_rating": "合法", "voltage_rating": "合法", "installation_type": "合法", "property_type": "合法"}
            )

        # 2. Smart Capacitors: NJK-0.45-30-3 or NJK-0.45-20.10-1
        m_njk = re.match(r'^(NJK)-([\d\.]+)-([\d\.]+)-?([13])?', s)
        if m_njk:
            series = m_njk.group(1)
            volt_num = m_njk.group(2)
            cap_num = m_njk.group(3)
            phase_char = m_njk.group(4) or "3"
            phase_name = "三相共补" if phase_char == "3" else "分相补偿"

            data = {
                "product_model": series,
                "voltage_rating": f"{volt_num}kV" if not volt_num.endswith('kV') else volt_num,
                "capacity_rating": f"{cap_num}kvar",
                "phase_type": phase_name,
                "property_type": "本体"
            }
            return PQParseResult(
                raw_input=raw_input, clean_model=s, is_valid=True, parse_status="成功",
                data=data,
                field_validations={"product_model": "合法", "voltage_rating": "合法", "capacity_rating": "合法", "phase_type": "合法", "property_type": "合法"}
            )

        # 3. Switching Capacitor Contactors: CJ19-32/11 or CJ19-43/21
        m_cj19 = re.match(r'^(CJ19)-(\d+)/(\d+)', s)
        if m_cj19:
            series = m_cj19.group(1)
            current_rating = f"{m_cj19.group(2)}A"
            contact_type = f"触头 {m_cj19.group(3)}"
            data = {
                "product_model": series,
                "capacity_rating": current_rating,
                "voltage_rating": "380V",
                "installation_type": "固定式",
                "phase_type": contact_type,
                "property_type": "本体"
            }
            return PQParseResult(
                raw_input=raw_input, clean_model=s, is_valid=True, parse_status="成功",
                data=data,
                field_validations={"product_model": "合法", "capacity_rating": "合法", "voltage_rating": "合法", "installation_type": "合法", "phase_type": "合法", "property_type": "合法"}
            )

        return PQParseResult(
            raw_input=raw_input, clean_model=s, is_valid=False, parse_status="解析失败：型号格式不匹配",
            data={"product_model": "未知", "property_type": "待确认"},
            field_validations={"format": "格式不匹配"}
        )
