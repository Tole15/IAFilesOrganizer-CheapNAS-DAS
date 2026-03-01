from pydantic import BaseModel
from typing import Optional

class SearchHit(BaseModel):
    file_id: int
    path: str
    score: float
    content_preview: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    top_k: int
    hits: list[SearchHit]