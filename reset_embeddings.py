from packages.core.db import SessionLocal
from packages.core.models import FileEntry

db = SessionLocal()
try:
    rows = db.query(FileEntry).filter(FileEntry.embedding_status == "error").all()
    print("Errors found:", len(rows))
    for r in rows:
        r.embedding_status = "pending"
        r.embedding_error = None
        r.embedding = None
        r.embedding_dim = None
        r.embedding_model = None
    db.commit()
    print("Reset done.")
finally:
    db.close()