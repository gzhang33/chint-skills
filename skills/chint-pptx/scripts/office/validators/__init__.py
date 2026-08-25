"""
Validation modules for PPTX presentation processing.
"""

from .base import BaseSchemaValidator
from .pptx import PPTXSchemaValidator

__all__ = [
    "BaseSchemaValidator",
    "PPTXSchemaValidator",
]
