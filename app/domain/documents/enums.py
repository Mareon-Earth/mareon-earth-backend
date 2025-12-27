import enum


class DocumentType(str, enum.Enum):
    CSR = "CSR"
    GA_PLAN = "GA_PLAN"
    MACHINERY_LIST = "MACHINERY_LIST"
    SURVEY_REPORT = "SURVEY_REPORT"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"


class DocumentProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"
