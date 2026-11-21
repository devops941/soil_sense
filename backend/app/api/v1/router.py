from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    analysis,
    classification,
    dashboard,
    exports,
    locations,
    parameters,
    reports,
    samples,
    statistics,
    thresholds,
    uploads,
)

api_router = APIRouter()

api_router.include_router(samples.router)
api_router.include_router(uploads.router)
api_router.include_router(classification.router)
api_router.include_router(analysis.router)
api_router.include_router(statistics.router)
api_router.include_router(locations.router)
api_router.include_router(thresholds.router)
api_router.include_router(parameters.router)
api_router.include_router(dashboard.router)
api_router.include_router(exports.router)
api_router.include_router(reports.router)
