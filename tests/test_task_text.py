"""Tests for turning text into tasks and tasks into text."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from personal_assistant.task_text import format_task_line, parse_add_args
from personal_assistant.tasks import add_task, connect, list_open_tasks

AMSTERDAM = ZoneInfo("Europe/Amsterdam")


# --- parse_add_args ---


def test_parse_add_args_with_date_and_time():
    title, due_at = parse_add_args(["2026-11-06", "15:00", "Dentist"], AMSTERDAM)
    assert title == "Dentist"
    assert due_at == datetime(2026, 11, 6, 15, 0, tzinfo=AMSTERDAM)


def test_parse_add_args_keeps_multi_word_title():
    title, _ = parse_add_args(
        ["2026-11-06", "15:00", "Call", "the", "dentist"], AMSTERDAM
    )
    assert title == "Call the dentist"


def test_parse_add_args_without_time():
    title, due_at = parse_add_args(["Pay", "the", "bill"], AMSTERDAM)
    assert title == "Pay the bill"
    assert due_at is None


def test_parse_add_args_rejects_empty_title():
    with pytest.raises(ValueError):
        parse_add_args([], AMSTERDAM)


def test_parse_add_args_treats_bad_date_as_title():
    title, due_at = parse_add_args(["2026-13-45", "99:99", "Dentist"], AMSTERDAM)
    assert title == "2026-13-45 99:99 Dentist"
    assert due_at is None


# --- format_task_line ---


def test_format_task_line_with_due_time_shows_local_time():
    conn = connect(":memory:")
    add_task(conn, "Dentist", datetime(2026, 11, 6, 15, 0, tzinfo=AMSTERDAM))
    task = list_open_tasks(conn)[0]
    assert format_task_line(task, AMSTERDAM) == "#1 06.11 15:00 Dentist"


def test_format_task_line_without_due_time():
    conn = connect(":memory:")
    add_task(conn, "Pay the bill")
    task = list_open_tasks(conn)[0]
    assert format_task_line(task, AMSTERDAM) == "#1 Pay the bill"
