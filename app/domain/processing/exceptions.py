from fastapi import status
from app.core.exceptions.base import MareonError


class ParsingJobNotFound(MareonError):
    message = "Parsing job not found."
    code = "PARSING_JOB_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND

class ParsingJobAlreadyExistsError(MareonError):
    message = "Parsing job already exists."
    code = "PARSING_JOB_ALREADY_EXISTS"
    status_code = status.HTTP_409_CONFLICT



__all__ = ["ParsingJobNotFound", "ParsingJobAlreadyExistsError"]