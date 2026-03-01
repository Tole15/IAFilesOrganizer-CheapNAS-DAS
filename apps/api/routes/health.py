from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from packages.core.db import get_db
from packages.core.config import OPENAI_EMBED_MODEL
from packages.intelligence.openai_embed import embed_text

router = APIRouter()

@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        db_err = None
    except Exception as e:
        db_ok = False
        db_err = str(e)

    try:
        _ = embed_text("ping", model=OPENAI_EMBED_MODEL)
        openai_ok = True
        openai_err = None
    except Exception as e:
        openai_ok = False
        openai_err = str(e)

    return {
        "db_ok": db_ok,
        "db_error": db_err,
        "openai_ok": openai_ok,
        "openai_error": openai_err,
        "embed_model": OPENAI_EMBED_MODEL,
    }