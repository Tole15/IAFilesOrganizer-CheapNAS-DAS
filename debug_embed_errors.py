from packages.core.db import SessionLocal
from packages.core.models import FileEntry

def main():
    db = SessionLocal()
    try:
        rows = (
            db.query(FileEntry)
            .filter(FileEntry.embedding_status == "error")
            .order_by(FileEntry.id.desc())
            .limit(10)
            .all()
        )
        if not rows:
            print("No rows with embedding_status='error'")
            return

        for r in rows:
            print("ID:", r.id)
            print("PATH:", r.path)
            print("ERR:", r.embedding_error)
            print("-" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    main()