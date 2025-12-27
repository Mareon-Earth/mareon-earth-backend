# app/infrastructure/db/mixins.py
from __future__ import annotations

from app.infrastructure.db.sa import (
    String,
    TIMESTAMP,
    ForeignKey,
    Mapped,
    mapped_column,
    text,
)


class UUIDPrimaryKeyMixin:
    """Adds `id` primary key with server-side UUID default."""
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )


class CreatedAtMixin:
    """Adds `created_at` timestamp."""
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class UpdatedAtMixin:
    """Adds `updated_at` timestamp."""
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )


class TimestampsMixin(CreatedAtMixin, UpdatedAtMixin):
    """Adds `created_at` and `updated_at` timestamps."""
    pass


class OrgScopedMixin:
    """Adds `org_id` FK for tenant scoping."""
    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )


class CreatedByUserMixin:
    """Adds `created_by` FK to users; sets NULL if user is deleted."""
    created_by: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
