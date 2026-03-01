import sqlite3

DB_PATH = "./data/index.db"

SQL = """
CREATE TABLE IF NOT EXISTS op_journal (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plan_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'done',
  ops_json TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_op_journal_plan_id ON op_journal(plan_id);
"""

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.executescript(SQL)
conn.commit()
conn.close()
print("op_journal table OK")