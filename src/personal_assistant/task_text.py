import sqlite3
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_FORMAT = "%d.%m %H:%M"


def parse_add_args(args: list[str], tz: tzinfo) -> tuple[str, datetime | None]:
    """Parse the words after /add into a title and an optional due time.

    "/add 2026-11-06 15:00 Dentist" -> ("Dentist", 2026-11-06 15:00 in tz)
    "/add Pay the bill"             -> ("Pay the bill", None)
    """

    if len(args) >= 3:
        try:
            naive = datetime.strptime(f"{args[0]} {args[1]}", DATE_TIME_FORMAT)
        except ValueError:
            pass
        else:
            return " ".join(args[2:]), naive.replace(tzinfo=tz)

    title = " ".join(args)
    if not title:
        raise ValueError("title is empty")

    return title, None


def format_task_line(task: sqlite3.Row, tz: tzinfo) -> str:
    """Format one task for display, e.g. "#3 06.11 15:00 Dentist"."""
    if task["due_at"] is None:
        return f"#{task['id']} {task['title']}"

    due_at_utc = datetime.fromisoformat(task["due_at"])
    due_at_local = due_at_utc.astimezone(tz)
    time_text = due_at_local.strftime(DISPLAY_FORMAT)
    return f"#{task['id']} {time_text} {task['title']}"


amsterdam = ZoneInfo("Europe/Amsterdam")

task_1 = {"id": "1", "title": "Dentist", "due_at": "2026-11-06T14:00:00+00:00"}
task_2 = {"id": "1", "title": "Pay the bill"}
