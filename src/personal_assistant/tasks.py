import sqlite3
from datetime import UTC, datetime

SCHEMA = """ 
    CREATE TABLE IF NOT EXISTS tasks (
        id          INTEGER PRIMARY KEY,
        title       TEXT NOT NULL,
        due_at      TEXT,
        remind_at   TEXT,
        reminded_at TEXT,
        done_at     TEXT,
        created_at  TEXT NOT NULL
    )
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _to_utc_text(moment: datetime) -> str:
    if moment.tzinfo is None:
        raise ValueError("datetime must have a timezone")
    return moment.astimezone(UTC).isoformat()


def add_task(
    conn: sqlite3.Connection, title: str, due_at: datetime | None = None
) -> int:
    """Add a task and return its id."""
    if due_at is not None:
        due_at_text = _to_utc_text(due_at)
    else:
        due_at_text = None
    cursor = conn.execute(
        "INSERT INTO tasks (title, due_at, created_at) VALUES (?,?,?)",
        (title, due_at_text, _utc_now()),
    )
    conn.commit()
    return cursor.lastrowid


def list_open_tasks(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all open tasks, the earliest due first."""
    query = """
    SELECT id, title, due_at
    FROM tasks
    WHERE done_at IS NULL
    ORDER BY due_at IS NULL, due_at
    """
    return conn.execute(query).fetchall()


def complete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    cursor = conn.execute(
        "UPDATE tasks SET done_at = ? WHERE id = ? AND done_at IS NULL",
        (_utc_now(), task_id),
    )
    conn.commit()
    return cursor.rowcount == 1
