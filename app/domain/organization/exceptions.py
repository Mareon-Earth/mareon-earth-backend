from fastapi import status
from app.core.exceptions.base import MareonError


class OrganizationNotFoundError(MareonError):
    message = "Organization not found."
    code = "ORGANIZATION_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class OrganizationMemberNotFoundError(MareonError):
    message = "Organization member not found."
    code = "ORGANIZATION_MEMBER_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
