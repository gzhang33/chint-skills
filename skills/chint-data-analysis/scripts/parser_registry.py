#!/usr/bin/env python3
"""
CHINT Integrated Analytics - Central Parser Registry & Factory
Path: etl/parser_registry.py

Provides unified access to category-specific deterministic model parsers (ACB, ATSE, MCCB, PQ, VF).
"""

from typing import Dict, Any, Optional
from etl.base_parser import BaseModelParser
from etl.mccb_parser import get_mccb_parser, clear_mccb_parser_cache
from etl.acb_parser import get_acb_parser, clear_acb_parser_cache
from etl.atse_parser import get_atse_parser, clear_atse_parser_cache
from etl.pq_parser import get_pq_parser, clear_pq_parser_cache
from etl.vf_parser import get_vf_parser, clear_vf_parser_cache


def get_parser(department: Optional[str] = "mccb") -> BaseModelParser:
    """
    Returns dedicated singleton parser for specified product category/department.
    """
    dept = (department or "mccb").lower().strip()
    if dept == "acb":
        return get_acb_parser()
    elif dept == "atse":
        return get_atse_parser()
    elif dept == "pq":
        return get_pq_parser()
    elif dept == "vf":
        return get_vf_parser()
    else:
        return get_mccb_parser()


def clear_all_parser_caches():
    """Clears all in-memory SSOT configs and cached parser instances across all departments."""
    clear_mccb_parser_cache()
    clear_acb_parser_cache()
    clear_atse_parser_cache()
    clear_pq_parser_cache()
    clear_vf_parser_cache()

