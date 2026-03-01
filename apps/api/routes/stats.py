# apps/api/routes/stats.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from packages.core.db import get_db
from packages.core.models import FileEntry

router = APIRouter()

@router.get("/stats")
def stats(
    root_path: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(FileEntry)
    if root_path:
        q = q.filter(FileEntry.root_path == root_path)

    total = q.count()
    active = q.filter(FileEntry.status == "active").count()
    missing = q.filter(FileEntry.status == "missing").count()

    # extract
    pending_extract = q.filter(FileEntry.content_status == "pending").count()
    ok_extract = q.filter(FileEntry.content_status == "ok").count()
    unsupported_extract = q.filter(FileEntry.content_status == "unsupported").count()
    error_extract = q.filter(FileEntry.content_status == "error").count()

    # embed
    pending_embed = q.filter(FileEntry.embedding_status == "pending").count()
    ok_embed = q.filter(FileEntry.embedding_status == "ok").count()
    error_embed = q.filter(FileEntry.embedding_status == "error").count()

    return {
        "root_path": root_path,
        "files": {"total": total, "active": active, "missing": missing},
        "extract": {
            "pending": pending_extract,
            "ok": ok_extract,
            "unsupported": unsupported_extract,
            "error": error_extract,
        },
        "embed": {"pending": pending_embed, "ok": ok_embed, "error": error_embed},
    }