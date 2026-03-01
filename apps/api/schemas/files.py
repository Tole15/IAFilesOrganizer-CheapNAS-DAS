from pydantic import BaseModel
from typing import Optional

class FileResponse(BaseModel):
    id: int
    path: str
    root_path: str
    size_bytes: int
    mtime: int
    ctime: int
    sha256: Optional[str] = None
    mimetype: Optional[str] = None
    ext: Optional[str] = None
    status: str
    last_seen_job_id: Optional[int] = None
    content_status: Optional[str] = None
    content_error: Optional[str] = None
    content_preview: Optional[str] = None