# apps/api/routes/plan.py
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from apps.api.schemas.plan import PlanRequest, PlanResponse
from packages.core.db import get_db, SessionLocal
from packages.core.jobs import create_plan_job, run_plan_job

router = APIRouter()


@router.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    job = create_plan_job(db, req.root_path, req.policy, req.limit)
    bg.add_task(_run_plan_in_new_session, job.id, req.policy, req.limit, req.exclude_globs)
    return PlanResponse(job_id=job.id, status="queued")


def _run_plan_in_new_session(job_id: int, policy: str, limit: int, exclude_globs: list[str]):
    db = SessionLocal()
    try:
        run_plan_job(db, job_id, policy=policy, limit=limit, exclude_globs=exclude_globs)
    finally:
        db.close()