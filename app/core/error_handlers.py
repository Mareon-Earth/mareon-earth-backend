from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions.base import MareonError


def register_error_handlers(app: FastAPI):
    @app.exception_handler(MareonError)
    async def mareon_handler(request: Request, exc: MareonError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    **exc.to_dict(),
                    "status_code": exc.status_code,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Invalid request payload.",
                    "code": "VALIDATION_ERROR",
                    "details": exc.errors(),
                    "status_code": 422,
                }
            },
        )

    @app.exception_handler(Exception)
    async def fallback_handler(request: Request, exc: Exception):
        # TODO: integrate Sentry / GCP Error Reporting
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred.",
                    "code": "INTERNAL_ERROR",
                    "status_code": 500,
                }
            },
        )
