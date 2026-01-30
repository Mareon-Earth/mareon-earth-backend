from __future__ import annotations

from enum import Enum


class DocumentContentType(str, Enum):
    PDF = "PDF"
    IMAGE = "IMAGE"
    DOCX = "DOCX"
    XLSX = "XLSX"
    CSV = "CSV"
    PPTX = "PPTX"
    TXT = "TXT"
    OTHER = "OTHER"


class DocumentType(str, Enum):
    CLASS_STATUS_REPORT = "CLASS_STATUS_REPORT"
    GA_PLAN = "GA_PLAN"
    MACHINERY_LIST = "MACHINERY_LIST"
    SURVEY_REPORT = "SURVEY_REPORT"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"


class ParsingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"

__all__ = ["DocumentContentType", "DocumentType", "ParsingStatus"]