from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import DBSession
from backend.database import Plannable
from backend.schemas import PlannableSchema

router = APIRouter()

@router.get("/", response_model=List[PlannableSchema], operation_id="readPlannables")
def read_plannables(db: DBSession, request:PlannableSchema) -> PlannableSchema:
    return db.query(Plannable).all()


@router.get("/{plannable_id}", response_model=PlannableSchema, operation_id="readPlannable")
def read_plannable(plannable_id: int, db: DBSession, request:PlannableSchema) -> PlannableSchema:
    plannable = db.query(Plannable).filter(Plannable.id == plannable_id).first()
    if not plannable:
        raise HTTPException(status_code=404, detail="Plannable not found")
    return plannable