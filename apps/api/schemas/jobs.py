from pydantic import BaseModel
from typing import Optional

class JobResponse(BaseModel):
    id: int
    type: str
    status: str
    root_path: str
    mode: str
    stats_json: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    created_at: Optional[str] = None