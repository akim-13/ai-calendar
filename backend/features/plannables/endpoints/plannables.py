from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import DBSession
from backend.database import get_db, Plannable
from backend.schemas import CreatePlannableRequest, UpdatePlannableRequest, PlannableSchema

router = APIRouter()

@router.post("/", response_model=PlannableSchema)
def create_plannable(request: CreatePlannableRequest, db: Session = Depends(get_db)):
    new_plannable = Plannable(
        username=request.username,
        external_calendar_id=request.external_calendar_id,
        type=request.type,
        title=request.title,
        description=request.description,
        is_completed=request.is_completed or False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_plannable)
    db.commit()
    db.refresh(new_plannable)
    return new_plannable


@router.get("/", response_model=List[PlannableSchema])
def read_plannables(db: Session = Depends(get_db)):
    return db.query(Plannable).all()


@router.get("/{plannable_id}", response_model=PlannableSchema)
def read_plannable(plannable_id: int, db: Session = Depends(get_db)):
    plannable = db.query(Plannable).filter(Plannable.id == plannable_id).first()
    if not plannable:
        raise HTTPException(status_code=404, detail="Plannable not found")
    return plannable


@router.put("/{plannable_id}", response_model=PlannableSchema)
def update_plannable(plannable_id: int, request: UpdatePlannableRequest, db: Session = Depends(get_db)):
    plannable = db.query(Plannable).filter(Plannable.id == plannable_id).first()
    if not plannable:
        raise HTTPException(status_code=404, detail="Plannable not found")

    plannable.title = request.title or plannable.title
    plannable.description = request.description or plannable.description
    plannable.type = request.type or plannable.type
    plannable.is_completed = request.is_completed if request.is_completed is not None else plannable.is_completed
    plannable.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(plannable)
    return plannable


@router.delete("/{plannable_id}")
def delete_plannable(plannable_id: int, db: Session = Depends(get_db)):
    plannable = db.query(Plannable).filter(Plannable.id == plannable_id).first()
    if not plannable:
        raise HTTPException(status_code=404, detail="Plannable not found")

    db.delete(plannable)
    db.commit()
    return {"detail": "Plannable deleted successfully"}