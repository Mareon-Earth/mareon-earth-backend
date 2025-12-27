"""
Domain models registry.
Import all models here to ensure they're registered with SQLAlchemy metadata.
"""
from app.domain.users.models import User
from app.domain.organization.models import Organization, OrganizationMember

__all__ = [
    "User",
    "Organization",
    "OrganizationMember",
]