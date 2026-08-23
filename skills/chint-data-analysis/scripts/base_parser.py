#!/usr/bin/env python3
"""
CHINT Integrated Analytics - Universal Base Parser Framework
Path: etl/base_parser.py

Provides common base dataclasses, text sanitization, and batch execution logic for all product categories.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class BaseParseResult:
    raw_input: str
    clean_model: str
    is_valid: bool
    parse_status: str
    data: Dict[str, str] = field(default_factory=dict)
    field_validations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseModelParser:
    """Base class providing common batch parsing and summary aggregation."""

    def parse(self, text: str) -> BaseParseResult:
        raise NotImplementedError("Subclasses must implement parse method")

    def batch_parse(self, items: List[str]) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []
        success_count = 0
        invalid_count = 0
        body_count = 0
        accessory_count = 0
        unknown_series_count = 0
        format_mismatch_count = 0

        for text in items:
            res = self.parse(text)
            rec = res.to_dict()
            records.append(rec)

            if res.is_valid:
                success_count += 1
            else:
                invalid_count += 1

            prop = res.data.get("property_type", "")
            if prop == "本体":
                body_count += 1
            elif prop == "附件":
                accessory_count += 1

            if "未知系列" in res.parse_status:
                unknown_series_count += 1
            if "型号格式不匹配" in res.parse_status:
                format_mismatch_count += 1

        total = len(items)
        success_rate = round((success_count / total * 100), 2) if total > 0 else 0.0

        return {
            "total": total,
            "success_count": success_count,
            "invalid_count": invalid_count,
            "success_rate": success_rate,
            "summary": {
                "body_count": body_count,
                "accessory_count": accessory_count,
                "unknown_series_count": unknown_series_count,
                "format_mismatch_count": format_mismatch_count
            },
            "records": records
        }
