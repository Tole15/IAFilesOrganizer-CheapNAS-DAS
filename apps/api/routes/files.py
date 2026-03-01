from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from apps.api.schemas.files import FileResponse
from packages.core.db import get_db
from packages.core.models import FileEntry

router = APIRouter()

def _preview(text: str | None, n: int = 800) -> str | None:
    if not text:
        return None
    return text[:n]

@router.get("/files", response_model=list[FileResponse])
def list_files(
    root_path: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(FileEntry)
    if root_path:
        q = q.filter(FileEntry.root_path == root_path)

    rows = q.order_by(FileEntry.id.desc()).offset(offset).limit(limit).all()

    return [
        FileResponse(
            id=r.id,
            path=r.path,
            root_path=r.root_path,
            size_bytes=r.size_bytes,
            mtime=r.mtime,
            ctime=r.ctime,
            sha256=r.sha256,
            mimetype=r.mimetype,
            ext=r.ext,
            status=r.status,
            last_seen_job_id=r.last_seen_job_id,

           
            content_status=getattr(r, "content_status", None),
            content_error=getattr(r, "content_error", None),
            content_preview=_preview(getattr(r, "content_text", None)),
        )
        for r in rows
    ]

@router.get("/files/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    r = db.query(FileEntry).filter(FileEntry.id == file_id).one_or_none()
    if r is None:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        id=r.id,
        path=r.path,
        root_path=r.root_path,
        size_bytes=r.size_bytes,
        mtime=r.mtime,
        ctime=r.ctime,
        sha256=r.sha256,
        mimetype=r.mimetype,
        ext=r.ext,
        status=r.status,
        last_seen_job_id=r.last_seen_job_id,

        
        content_status=getattr(r, "content_status", None),
        content_error=getattr(r, "content_error", None),
        content_preview=_preview(getattr(r, "content_text", None)),
    )