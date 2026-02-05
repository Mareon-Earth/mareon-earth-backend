"""
Shared type aliases for the domain layer.

Date/DateTime Convention:
- Use `Date` for `datetime.date` and `DateTime` for `datetime.datetime`.
- In SQLAlchemy models: Use `Mapped[Date | None]` or `Mapped[DateTime | None]`.
- In Pydantic schemas: Use `Date` or `DateTime` directly.
- In `mapped_column()`: Use `sa.Date` or `sa.DateTime`.
"""
from datetime import date, datetime
from typing import TypeAlias

UserId: TypeAlias = str
OrganizationId: TypeAlias = str
DocumentId: TypeAlias = str
DocumentFileId: TypeAlias = str
VesselId: TypeAlias = str
CertificateId: TypeAlias = str

OrganizationMemberId: TypeAlias = tuple[str, str]

ClerkUserId: TypeAlias = str
ClerkOrganizationId: TypeAlias = str
StoragePath: TypeAlias = str
SourceUri: TypeAlias = str  # Full GCS URI (gs://bucket/path)

ParsingJobId: TypeAlias = str

# Re-export for convenience - use these throughout the codebase
Date: TypeAlias = date
DateTime: TypeAlias = datetime