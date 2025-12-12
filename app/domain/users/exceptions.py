from fastapi import status
from app.core.exceptions.base import MareonError


class UserNotFoundError(MareonError):
    message = "User not found."
    code = "USER_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class UserAlreadyExistsError(MareonError):
    message = "User already exists."
    code = "USER_ALREADY_EXISTS"
    status_code = status.HTTP_409_CONFLICT
