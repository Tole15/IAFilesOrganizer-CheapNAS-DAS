from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from apps.api.schemas.extract import ExtractRequest, ExtractResponse
from packages.core.db import get_db, SessionLocal
from packages.core.jobs import create_extract_job, run_extract_job

router = APIRouter()

@router.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    job = create_extract_job(db, req.root_path)
    bg.add_task(_run_extract_in_new_session, job.id, req.limit, req.force)
    return ExtractResponse(job_id=job.id, status="queued")

def _run_extract_in_new_session(job_id: int, limit: int, force: bool):
    db = SessionLocal()
    try:
        run_extract_job(db, job_id, limit=limit, force=force)
    finally:
        db.close()