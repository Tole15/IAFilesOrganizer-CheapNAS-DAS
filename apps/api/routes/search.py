# apps/api/routes/search.py
import time
import numpy as np
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from packages.core.db import get_db
from packages.core.models import FileEntry
from packages.core.config import OPENAI_EMBED_MODEL
from packages.intelligence.openai_embed import embed_text
from packages.intelligence.embedding_io import unpack_embedding
from packages.intelligence.text_clean import clean_text

from apps.api.schemas.search import SearchResponse, SearchHit

router = APIRouter()

# Cache simple en memoria para embeddings de query (TTL)
_QUERY_CACHE: dict[str, tuple[float, np.ndarray]] = {}
_QUERY_CACHE_TTL_SEC = 600  # 10 min

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

def get_query_embedding(q: str) -> np.ndarray:
    now = time.time()
    cached = _QUERY_CACHE.get(q)
    if cached:
        ts, vec = cached
        if (now - ts) < _QUERY_CACHE_TTL_SEC:
            return vec

    q_clean = clean_text(q, max_len=4000)  # query más corto
    vec = np.array(embed_text(q_clean, model=OPENAI_EMBED_MODEL), dtype=np.float32)
    _QUERY_CACHE[q] = (now, vec)
    return vec

@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(min_length=1),
    root_path: str | None = Query(default=None),
    ext: str | None = Query(default=None, description="Filter by extension, e.g. pdf"),
    top_k: int = Query(default=5, ge=1, le=20),
    min_score: float = Query(default=0.0, ge=-1.0, le=1.0),
    include_preview: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    # 1) embedding del query (cacheado)
    qvec = get_query_embedding(q)

    # 2) cargar candidatos con embedding
    qdb = db.query(FileEntry).filter(
        FileEntry.embedding_status == "ok",
        FileEntry.embedding.isnot(None),
        FileEntry.status == "active",
    )
    if root_path:
        qdb = qdb.filter(FileEntry.root_path == root_path)
    if ext:
        qdb = qdb.filter(FileEntry.ext == ext.lower().lstrip("."))

    rows = qdb.all()

    scored = []
    for r in rows:
        vec = unpack_embedding(r.embedding)
        s = cosine(qvec, vec)
        if s < min_score:
            continue

        preview = None
        if include_preview and getattr(r, "content_text", None):
            preview = r.content_text[:800]

        scored.append((s, r.id, r.path, preview))

    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [
        SearchHit(file_id=file_id, path=path, score=score, content_preview=preview)
        for score, file_id, path, preview in scored[:top_k]
    ]

    return SearchResponse(query=q, top_k=top_k, hits=hits)