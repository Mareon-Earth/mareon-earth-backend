from app.domain._shared.errors import Conflict, NotFound, DomainError


class VesselNotFoundError(NotFound):
    code = "VESSEL_NOT_FOUND"
    message = "Vessel not found."

class VesselAlreadyExistsError(Conflict):
    code = "VESSEL_ALREADY_EXISTS"
    message = "Vessel already exists."

class VesselInvalidDataError(DomainError):
    code = "VESSEL_INVALID_DATA"
    message = "Invalid vessel data."