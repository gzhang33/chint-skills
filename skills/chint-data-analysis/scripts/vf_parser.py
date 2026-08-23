#!/usr/bin/env python3
"""
CHINT Integrated Analytics - VF (Virtual Factory) & OEM Deterministic Model Parser
Path: etl/vf_parser.py

Strict, high-performance deterministic grammar parser for Virtual Factory & OEM models.
"""

import os
import re
from typing import Dict, Any, List, Optional
from etl.base_parser import BaseParseResult, BaseModelParser
from etl.mccb_parser import get_mccb_parser


class VFParseResult(BaseParseResult):
    pass


_SINGLETON_VF_PARSER: Optional["VFModelParser"] = None


def clear_vf_parser_cache():
    global _SINGLETON_VF_PARSER
    _SINGLETON_VF_PARSER = None


def get_vf_parser() -> "VFModelParser":
    global _SINGLETON_VF_PARSER
    if _SINGLETON_VF_PARSER is None:
        _SINGLETON_VF_PARSER = VFModelParser()
    return _SINGLETON_VF_PARSER


class VFModelParser(BaseModelParser):
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        pass

    def parse(self, text: str) -> VFParseResult:
        raw_input = str(text or "").strip()
        if not raw_input:
            return VFParseResult(raw_input="", clean_model="", is_valid=False, parse_status="解析失败：输入为空", data={}, field_validations={})

        s = re.sub(r'^特[\s\-_]*', '', raw_input).strip()
        mccb_engine = get_mccb_parser()
        
        # Check prefix: OEM-, VF-, ODM- or custom prefix
        partner_code = "OEM"
        base_model_text = s
        prefix_m = re.match(r'^([A-Za-z0-9]{2,8})-([A-Za-z0-9].*)$', s)
        if prefix_m:
            candidate_prefix = prefix_m.group(1).upper()
            # If the candidate prefix itself is a known MCCB series (e.g. NXM, NM1, DZ20), then it's NOT a partner code
            if candidate_prefix in mccb_engine.legal_series or candidate_prefix.startswith(("NXM", "NM1", "NM8", "DZ20", "NXMP")):
                partner_code = "CHINT"
                base_model_text = s
            else:
                partner_code = candidate_prefix
                base_model_text = prefix_m.group(2)
        else:
            partner_code = "CHINT"

        # Delegate base breaker parsing to MCCB parser
        mccb_res = mccb_engine.parse(base_model_text)
        data = dict(mccb_res.data)
        data["partner_code"] = partner_code

        validations = dict(mccb_res.field_validations)
        validations["partner_code"] = "合法"

        return VFParseResult(
            raw_input=raw_input,
            clean_model=s,
            is_valid=mccb_res.is_valid,
            parse_status=mccb_res.parse_status,
            data=data,
            field_validations=validations
        )
