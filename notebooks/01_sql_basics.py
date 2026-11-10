import sqlite3
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

conn.execute("""
    CREATE TABLE tasks (
        id              INTEGER PRIMARY KEY,
        title           TEXT NOT NULL,
        due_at          TEXT,
        remind_at       TEXT,
        reminded_at     TEXT,
        done_at         TEXT,
        created_at      TEXT NOT NULL
    )
""")

created_at = datetime.now(UTC).isoformat()

conn.execute(
    "INSERT INTO tasks (title, due_at, created_at) VALUES (?, ?, ?)",
    ("Dentist", "2026-11-06T14:00:00+00:00", created_at),
)
conn.execute(
    "INSERT INTO tasks (title, created_at) VALUES (?, ?)",
    ("Pay the bill", created_at),
)

conn.execute(
    "INSERT INTO tasks (title, created_at) VALUES (?, ?)",
    ("Call mom", created_at),
)

conn.execute(
    "INSERT INTO tasks (title, due_at, created_at) VALUES (?, ?, ?)",
    ("Gym", "2026-11-07T08:30:00+00:00", created_at),
)

print("All tasks:")
for row in conn.execute("SELECT id, title, due_at, done_at FROM tasks"):
    print(dict(row))

done_at = datetime.now(UTC).isoformat()
conn.execute("UPDATE tasks SET done_at = ? WHERE id = ?", (done_at, 1))

print("\nOpen tasks:")
for row in conn.execute("SELECT id, title FROM tasks WHERE done_at IS NULL"):
    print(dict(row))

print("\nTasks with time slot")

query = """
    SELECT id, title, due_at
    FROM tasks
    WHERE due_at IS NOT NULL AND done_at IS NULL
    ORDER BY due_at
"""

for row in conn.execute(query):
    due_at_utc = datetime.fromisoformat(row["due_at"])
    due_at_local = due_at_utc.astimezone(ZoneInfo("Europe/Amsterdam"))
    formatted = due_at_local.strftime("%d.%m.%Y %H:%M")
    print(f"{row['title']}: {formatted}")
