import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from packages.core.db import get_db
from packages.core.models import Plan
from apps.api.schemas.apply import ApplyRequest, ApplyResponse
from packages.executor.apply import apply_plan

router = APIRouter()

@router.post("/apply", response_model=ApplyResponse)
def apply(req: ApplyRequest, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == req.plan_id).one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan = json.loads(p.plan_json)
    journal = apply_plan(plan, dry_run=req.dry_run)

    return ApplyResponse(
        plan_id=req.plan_id,
        dry_run=req.dry_run,
        summary=journal["summary"],
        errors=journal["errors"],
    )