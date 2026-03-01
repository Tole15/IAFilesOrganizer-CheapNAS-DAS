from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from apps.api.schemas.scan import ScanRequest, ScanResponse
from packages.core.db import get_db
from packages.core.jobs import create_scan_job, run_scan_job

router = APIRouter()

@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    job = create_scan_job(db, req.root_path, req.mode)
    bg.add_task(_run_job_in_new_session, job.id)  # evita usar la misma sesión
    return ScanResponse(job_id=job.id, status="queued")

def _run_job_in_new_session(job_id: int):
    # Import local para evitar ciclos
    from packages.core.db import SessionLocal
    db = SessionLocal()
    try:
        run_scan_job(db, job_id)
    finally:
        db.close()