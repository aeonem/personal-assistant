"""Tests for the task storage module."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from personal_assistant.tasks import add_task, complete_task, connect, list_open_tasks


def test_add_task_returns_new_id():
    conn = connect(":memory:")

    first_id = add_task(conn, "Dentist")
    second_id = add_task(conn, "Gym")

    assert first_id == 1
    assert second_id == 2


def test_add_task_stores_due_time_in_utc():
    conn = connect(":memory:")
    amsterdam = ZoneInfo("Europe/Amsterdam")

    add_task(conn, "Dentist", datetime(2026, 11, 6, 15, 0, tzinfo=amsterdam))

    row = conn.execute("SELECT due_at FROM tasks").fetchone()
    assert row["due_at"] == "2026-11-06T14:00:00+00:00"


def test_add_task_rejects_naive_datetime():
    conn = connect(":memory:")

    with pytest.raises(ValueError):
        add_task(conn, "Dentist", datetime(2026, 11, 6, 15, 0))


def test_complete_task_unknown_id_returns_false():
    conn = connect(":memory:")

    assert complete_task(conn, 99) is False


def test_complete_task_twice_returns_false():
    conn = connect(":memory:")
    task_id = add_task(conn, "Gym")

    assert complete_task(conn, task_id) is True
    assert complete_task(conn, task_id) is False


def test_list_open_tasks_hides_done_tasks():
    conn = connect(":memory:")
    add_task(conn, "Pay the bill")
    gym_id = add_task(conn, "Gym")

    complete_task(conn, gym_id)

    titles = [task["title"] for task in list_open_tasks(conn)]
    assert titles == ["Pay the bill"]


def test_list_open_tasks_puts_timed_tasks_first_in_order():
    conn = connect(":memory:")
    utc = ZoneInfo("UTC")
    add_task(conn, "Pay the bill")
    add_task(conn, "Gym", datetime(2026, 11, 7, 8, 30, tzinfo=utc))
    add_task(conn, "Dentist", datetime(2026, 11, 6, 14, 0, tzinfo=utc))

    titles = [task["title"] for task in list_open_tasks(conn)]
    assert titles == ["Dentist", "Gym", "Pay the bill"]


def test_tasks_survive_reconnect(tmp_path):
    db_path = str(tmp_path / "test.db")

    conn = connect(db_path)
    add_task(conn, "Dentist")
    conn.close()

    conn = connect(db_path)
    titles = [task["title"] for task in list_open_tasks(conn)]
    assert titles == ["Dentist"]
