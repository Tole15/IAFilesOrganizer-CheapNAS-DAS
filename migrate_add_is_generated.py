import sqlite3

DB_PATH = "./data/index.db"

def column_exists(cur, table: str, col: str) -> bool:
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    return col in cols

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

TABLE = "files"  

if not column_exists(cur, TABLE, "is_generated"):
    cur.execute(f"ALTER TABLE {TABLE} ADD COLUMN is_generated INTEGER NOT NULL DEFAULT 0;")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_is_generated ON {TABLE}(is_generated);")
    conn.commit()
    print(f"OK: added {TABLE}.is_generated")
else:
    print(f"OK: {TABLE}.is_generated already exists")

conn.close()