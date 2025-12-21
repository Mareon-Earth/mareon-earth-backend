import enum

from app.infrastructure.db import Base
from app.infrastructure.db.sa import (
    String,
    ForeignKey,
    PrimaryKeyConstraint,
    Index,
    text,
    Mapped,
    mapped_column,
    relationship,
    SAEnum,
)
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin, TimestampsMixin, CreatedAtMixin


class OrganizationRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Organization(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "organization"

    clerk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str | None] = mapped_column(String, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Relationships to vessel and document domains
    vessels: Mapped[list["Vessel"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    
    documents: Mapped[list["Document"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )


class OrganizationMember(TimestampsMixin, Base):
    __tablename__ = "organization_member"

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[OrganizationRole] = mapped_column(
        SAEnum(OrganizationRole, name="org_role", native_enum=False),
        nullable=False,
        server_default=text(f"'{OrganizationRole.MEMBER.value}'"),
    )

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "org_id"),
        Index("ix_org_member_org_id", "org_id"),
        Index("ix_org_member_role", "role"),
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )

