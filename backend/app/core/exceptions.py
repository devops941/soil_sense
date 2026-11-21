from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class SoilSenseError(Exception):
    """Base exception for all SoilSense domain errors."""

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        self.message = message
        super().__init__(message)


class ValidationError(SoilSenseError):
    """Raised when incoming data fails domain validation."""


class MissingParameterError(SoilSenseError):
    """Raised when a required soil parameter is absent from a sample."""


class UnitMismatchError(SoilSenseError):
    """Raised when a parameter's unit does not match the expected standard."""


class NotFoundError(SoilSenseError):
    """Raised when a requested resource does not exist."""


class DuplicateError(SoilSenseError):
    """Raised when a unique-constraint violation is detected at the domain level."""


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


async def _not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def _validation_handler(request: Request, exc: SoilSenseError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


async def _duplicate_handler(request: Request, exc: DuplicateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


async def _base_handler(request: Request, exc: SoilSenseError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.message})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, _not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, _validation_handler)  # type: ignore[arg-type]
    app.add_exception_handler(MissingParameterError, _validation_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UnitMismatchError, _validation_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DuplicateError, _duplicate_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SoilSenseError, _base_handler)  # type: ignore[arg-type]
