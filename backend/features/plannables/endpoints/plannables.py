from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Sequence

from infra.db import DBSession
from backend.core.entities import Plannable
from backend.features.plannables.schemas.plannables import PlannableSchema

router = APIRouter(prefix="/plannables", tags=["Plannables"])

@router.get("/", response_model=List[PlannableSchema], operation_id="readPlannables")
def read_plannables(db: DBSession) -> List[PlannableSchema]:
    return db.query(PlannableSchema).all()


@router.get("/{plannable_id}", response_model=PlannableSchema, operation_id="readPlannable")
def read_plannable(plannable_id: int, db: DBSession) -> PlannableSchema:
    plannable = db.query(PlannableSchema).filter(Plannable.id == plannable_id).first()
    if not plannable:
        raise HTTPException(status_code=404, detail="Plannable not found")
    return plannable
