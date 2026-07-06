from datetime import datetime, time
from zoneinfo import ZoneInfo

from earnings_calendar_spreads.workflow.trading_loop_state import (
  has_job_run_today,
  mark_job_run_today,
  should_run_daily_job,
)


NEW_YORK_TIMEZONE = ZoneInfo("America/New_York")


def make_new_york_datetime(
  year: int,
  month: int,
  day: int,
  hour: int,
  minute: int,
) -> datetime:
  return datetime(
    year,
    month,
    day,
    hour,
    minute,
    tzinfo=NEW_YORK_TIMEZONE,
  )


def test_should_not_run_before_scheduled_time(tmp_path):
  path = tmp_path / "state.json"
  now = make_new_york_datetime(2026, 7, 6, 9, 30)

  assert should_run_daily_job(
    job_name="exit",
    scheduled_time=time(9, 45),
    new_york_now=now,
    path=path,
  ) is False


def test_should_run_after_scheduled_time(tmp_path):
  path = tmp_path / "state.json"
  now = make_new_york_datetime(2026, 7, 6, 9, 45)

  assert should_run_daily_job(
    job_name="exit",
    scheduled_time=time(9, 45),
    new_york_now=now,
    path=path,
  ) is True


def test_should_not_run_twice_same_day(tmp_path):
  path = tmp_path / "state.json"
  now = make_new_york_datetime(2026, 7, 6, 9, 45)

  mark_job_run_today(
    job_name="exit",
    new_york_now=now,
    path=path,
  )

  assert has_job_run_today(
    job_name="exit",
    new_york_now=now,
    path=path,
  ) is True

  assert should_run_daily_job(
    job_name="exit",
    scheduled_time=time(9, 45),
    new_york_now=now,
    path=path,
  ) is False


def test_should_skip_weekend(tmp_path):
  path = tmp_path / "state.json"
  saturday = make_new_york_datetime(2026, 7, 11, 15, 45)

  assert should_run_daily_job(
    job_name="entry",
    scheduled_time=time(15, 45),
    new_york_now=saturday,
    path=path,
  ) is False