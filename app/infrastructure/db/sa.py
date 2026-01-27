# app/infrastructure/db/sa.py
"""
Small SQLAlchemy 2.0 "prelude" so domain model files don't repeatedly import
a huge list of types/helpers from sqlalchemy/sqlalchemy.orm.
"""

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    BigInteger,
    Float,
    Numeric,
    Date,
    DateTime,
    TIMESTAMP,
    JSON,
    Enum as SAEnum,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    PrimaryKeyConstraint,
    Index,
    text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

__all__ = [
    # Column types
    "String",
    "Text",
    "Boolean",
    "Integer",
    "BigInteger",
    "Float",
    "Numeric",
    "Date",
    "DateTime",
    "TIMESTAMP",
    "JSON",
    # Constraints / indexes / helpers
    "SAEnum",
    "ForeignKey",
    "UniqueConstraint",
    "CheckConstraint",
    "PrimaryKeyConstraint",
    "Index",
    "text",
    # ORM
    "Mapped",
    "mapped_column",
    "relationship",
]
