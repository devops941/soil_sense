from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.parameter import ParameterDefinition
from app.schemas.parameter import ParameterDefinitionRead

router = APIRouter(prefix="/parameters", tags=["parameters"])


@router.get("", response_model=List[ParameterDefinitionRead], summary="List all parameter definitions")
def list_parameters(db: Session = Depends(get_db)) -> List[ParameterDefinitionRead]:
    params = db.query(ParameterDefinition).filter(ParameterDefinition.is_active == True).all()  # noqa: E712
    return [ParameterDefinitionRead.model_validate(p) for p in params]


@router.get("/{code}", response_model=ParameterDefinitionRead, summary="Get a parameter definition by code")
def get_parameter(code: str, db: Session = Depends(get_db)) -> ParameterDefinitionRead:
    param = db.query(ParameterDefinition).filter(ParameterDefinition.code == code).first()
    if param is None:
        raise NotFoundError(f"Parameter with code '{code}' not found.")
    return ParameterDefinitionRead.model_validate(param)
