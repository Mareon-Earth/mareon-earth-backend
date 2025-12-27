from fastapi import status
from app.core.exceptions.base import MareonError


class OrganizationNotFoundError(MareonError):
    message = "Organization not found."
    code = "ORGANIZATION_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class OrganizationAlreadyExistsError(MareonError):
    message = "Organization already exists."
    code = "ORGANIZATION_ALREADY_EXISTS"
    status_code = status.HTTP_409_CONFLICT


class OrgMemberNotFoundError(MareonError):
    message = "Organization member not found."
    code = "ORG_MEMBER_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class OrgMemberAlreadyExistsError(MareonError):
    message = "User is already a member of this organization."
    code = "ORG_MEMBER_ALREADY_EXISTS"
    status_code = status.HTTP_409_CONFLICT
