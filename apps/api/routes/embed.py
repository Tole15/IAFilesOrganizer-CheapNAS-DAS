from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from apps.api.schemas.embed import EmbedRequest, EmbedResponse
from packages.core.db import get_db, SessionLocal
from packages.core.jobs import create_embed_job, run_embed_job

router = APIRouter()

@router.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    job = create_embed_job(db, req.root_path, req.limit)
    bg.add_task(_run_embed_in_new_session, job.id, req.limit)
    return EmbedResponse(job_id=job.id, status="queued")

def _run_embed_in_new_session(job_id: int, limit: int):
    db = SessionLocal()
    try:
        run_embed_job(db, job_id, limit=limit)
    finally:
        db.close()