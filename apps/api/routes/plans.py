import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from packages.core.db import get_db
from packages.core.models import Plan

router = APIRouter()

@router.get("/plans")
def list_plans(
    root_path: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Plan).order_by(Plan.id.desc())
    if root_path:
        q = q.filter(Plan.root_path == root_path)
    rows = q.limit(limit).all()
    return [
        {
            "id": p.id,
            "root_path": p.root_path,
            "policy": p.policy,
            "status": p.status,
            "created_at": str(p.created_at),
        } for p in rows
    ]

@router.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    p = db.query(Plan).filter(Plan.id == plan_id).one_or_none()
    if p is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return json.loads(p.plan_json)