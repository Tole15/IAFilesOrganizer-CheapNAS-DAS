import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.core.db import get_db
from packages.core.models import Plan
from apps.api.schemas.undo import UndoRequest, UndoResponse
from packages.executor.apply import apply_plan
from packages.executor.undo import undo_ops

router = APIRouter()

@router.post("/undo", response_model=UndoResponse)
def undo(req: UndoRequest, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == req.plan_id).one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = json.loads(p.plan_json)


    journal = apply_plan(plan, dry_run=True)  
    result = undo_ops(journal, dry_run=req.dry_run)

    return UndoResponse(
        plan_id=req.plan_id,
        dry_run=req.dry_run,
        summary=result["summary"],
        errors=result["errors"],
    )