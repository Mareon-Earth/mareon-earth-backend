"""
Domain models registry.
Import all models here to ensure they're registered with SQLAlchemy metadata.
"""
# Only import models, not repositories or other dependencies
# This ensures SQLAlchemy metadata is populated without circular imports
from app.domain.users import models as _user_models
from app.domain.organization import models as _org_models
from app.domain.document import models as _document_models
__all__ = []