"""Vessel domain models."""

from sqlalchemy import String, Integer, Date, Boolean, BigInteger, TIMESTAMP, text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.db import Base


class Vessel(Base):
    """Core vessel record."""
    
    __tablename__ = "vessel"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    created_by: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    vessel_type: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="vessels")
    created_by_user: Mapped["User"] = relationship()
    identity: Mapped["VesselIdentity"] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan",
        uselist=False
    )
    dimensions: Mapped["VesselDimensions"] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan",
        uselist=False
    )
    tonnage: Mapped["VesselTonnage"] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan",
        uselist=False
    )
    companies: Mapped["VesselCompany"] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan",
        uselist=False  # One-to-one relationship
    )
    certificates: Mapped[list["VesselCertificate"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    surveys: Mapped[list["VesselSurvey"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    memoranda: Mapped[list["VesselMemorandum"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    conditions_of_class: Mapped[list["VesselConditionOfClass"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    machinery_items: Mapped[list["VesselMachineryItem"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    hull_items: Mapped[list["VesselHullItem"]] = relationship(
        back_populates="vessel",
        cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary="vessel_document",
        back_populates="vessels"
    )


class VesselIdentity(Base):
    """Detailed vessel identification, tonnage, and build information."""
    
    __tablename__ = "vessel_identity"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Identification
    imo_number: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    mmsi_number: Mapped[str | None] = mapped_column(String, nullable=True)
    call_sign: Mapped[str | None] = mapped_column(String, nullable=True)
    class_number: Mapped[str | None] = mapped_column(String, nullable=True)  # DNV distinctive_number / ABS class_number
    official_number: Mapped[str | None] = mapped_column(String, nullable=True)  # ABS flag state registry number
    vessel_name: Mapped[str | None] = mapped_column(String, nullable=True)
    flag_state: Mapped[str | None] = mapped_column(String, nullable=True)
    port_of_registry: Mapped[str | None] = mapped_column(String, nullable=True)

    # Class information
    class_society: Mapped[str | None] = mapped_column(String, nullable=True)
    class_notation: Mapped[str | None] = mapped_column(String, nullable=True)
    operational_status: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_names: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_letter: Mapped[str | None] = mapped_column(String, nullable=True)  # DNV
    equipment_number: Mapped[str | None] = mapped_column(String, nullable=True)  # ABS
    
    # Class state (ABS-specific)
    class_state: Mapped[str | None] = mapped_column(String, nullable=True)
    other_state: Mapped[str | None] = mapped_column(String, nullable=True)
    lifecycle_state: Mapped[str | None] = mapped_column(String, nullable=True)
    dual_class: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    previous_class_society: Mapped[str | None] = mapped_column(String, nullable=True)

    # Vessel type and description
    vessel_description: Mapped[str | None] = mapped_column(String, nullable=True)  # ABS detailed description

    # Build dates
    keel_laid_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    building_contract_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    commissioning_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[str | None] = mapped_column(Date, nullable=True)  # ABS

    # Construction info (ABS-specific)
    shipyard: Mapped[str | None] = mapped_column(String, nullable=True)
    hull_number: Mapped[str | None] = mapped_column(String, nullable=True)

    # Regulatory categories (ABS-specific)
    solas_category: Mapped[str | None] = mapped_column(String, nullable=True)
    marpol_category: Mapped[str | None] = mapped_column(String, nullable=True)
    ibc_igc_category: Mapped[str | None] = mapped_column(String, nullable=True)
    ism_category: Mapped[str | None] = mapped_column(String, nullable=True)

    # Additional notations and restrictions (ABS-specific)
    additional_notations: Mapped[str | None] = mapped_column(String, nullable=True)
    service_restrictions: Mapped[str | None] = mapped_column(String, nullable=True)
    record_comments: Mapped[str | None] = mapped_column(String, nullable=True)

    # Freeboard (ABS-specific - from Active row only)
    freeboard_assignment: Mapped[str | None] = mapped_column(String, nullable=True)
    freeboard_type: Mapped[str | None] = mapped_column(String, nullable=True)
    freeboard_displacement: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    freeboard_deadweight: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    freeboard_calculated: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    freeboard_state: Mapped[str | None] = mapped_column(String, nullable=True)

    # DNV-specific fields
    tanks_and_spaces_annual: Mapped[str | None] = mapped_column(String, nullable=True)

    # ABS condition status flags
    conditions_of_class_reported: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    statutory_conditions_reported: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    special_recommendations_reported: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    special_additional_requirements_reported: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="identity")


class VesselDimensions(Base):
    """Vessel physical dimensions."""
    
    __tablename__ = "vessel_dimensions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Principal dimensions (in meters)
    length_overall_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    length_between_perpendiculars: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    breadth_moulded_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    depth_moulded_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    summer_draft_m: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="dimensions")


class VesselTonnage(Base):
    """Vessel tonnage information."""
    
    __tablename__ = "vessel_tonnage"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Standard tonnage
    gross_tonnage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gross_tonnage_pre69: Mapped[int | None] = mapped_column(Integer, nullable=True)
    net_tonnage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadweight_tonnage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Suez Canal tonnage (ABS-specific)
    suez_gross_tonnage: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    suez_net_tonnage: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="tonnage")


class VesselCompany(Base):
    """Vessel company relationships (owner/manager/doc holder) - single row per vessel."""
    
    __tablename__ = "vessel_company"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        unique=True,  # One row per vessel
        nullable=False,
    )

    # Owner information
    owner_name: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_company_number: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_address: Mapped[str | None] = mapped_column(String, nullable=True)

    # Manager information
    manager_name: Mapped[str | None] = mapped_column(String, nullable=True)
    manager_company_number: Mapped[str | None] = mapped_column(String, nullable=True)
    manager_address: Mapped[str | None] = mapped_column(String, nullable=True)

    # DOC Holder information (ABS-specific)
    doc_holder_name: Mapped[str | None] = mapped_column(String, nullable=True)
    doc_holder_company_number: Mapped[str | None] = mapped_column(String, nullable=True)
    doc_holder_address: Mapped[str | None] = mapped_column(String, nullable=True)

    # ISM Manager information (ABS-specific)
    ism_manager_name: Mapped[str | None] = mapped_column(String, nullable=True)
    ism_manager_address: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="companies")


class VesselCertificate(Base):
    """Vessel certificates."""
    
    __tablename__ = "vessel_certificate"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # 'class' | 'statutory'
    certificate_type_detail: Mapped[str | None] = mapped_column(String, nullable=True)

    issue_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    issue_location: Mapped[str | None] = mapped_column(String, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="certificates")
    document: Mapped["Document"] = relationship()


class VesselSurvey(Base):
    """Vessel surveys."""
    
    __tablename__ = "vessel_survey"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # 'class' | 'statutory'
    survey_type: Mapped[str | None] = mapped_column(String, nullable=True)

    last_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    last_survey_location: Mapped[str | None] = mapped_column(String, nullable=True)
    next_survey_from: Mapped[str | None] = mapped_column(Date, nullable=True)
    next_survey_due: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="surveys")
    document: Mapped["Document"] = relationship()


class VesselMemorandum(Base):
    """Vessel memoranda."""
    
    __tablename__ = "vessel_memorandum"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    memo_reference: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)

    issued_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    issued_location: Mapped[str | None] = mapped_column(String, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="memoranda")
    document: Mapped["Document"] = relationship()


class VesselConditionOfClass(Base):
    """Vessel conditions of class."""
    
    __tablename__ = "vessel_condition_of_class"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    coc_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    coc_type: Mapped[str] = mapped_column(String, nullable=False)  # 'condition' | 'recommendation'
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)  # 'OPEN' | 'CLOSED'

    issued_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    closed_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="conditions_of_class")
    document: Mapped["Document"] = relationship()


class VesselMachineryItem(Base):
    """Vessel machinery items for detailed tracking."""
    
    __tablename__ = "vessel_machinery_item"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(String, nullable=True)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    last_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    next_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="machinery_items")
    document: Mapped["Document"] = relationship()


class VesselHullItem(Base):
    """Vessel hull items for detailed tracking."""
    
    __tablename__ = "vessel_hull_item"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(String, nullable=True)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    last_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    next_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="hull_items")
    document: Mapped["Document"] = relationship()
