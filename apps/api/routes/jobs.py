from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.api.schemas.jobs import JobResponse
from packages.core.db import get_db
from packages.core.models import Job

router = APIRouter()

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        root_path=job.root_path,
        mode=job.mode,
        stats_json=job.stats_json,
        error=job.error,
        started_at=str(job.started_at) if job.started_at else None,
        finished_at=str(job.finished_at) if job.finished_at else None,
        created_at=str(job.created_at) if job.created_at else None,
    )