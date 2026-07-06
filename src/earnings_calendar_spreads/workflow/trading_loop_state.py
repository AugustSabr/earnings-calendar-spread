import json
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo


NEW_YORK_TIMEZONE = ZoneInfo("America/New_York")
DEFAULT_TRADING_LOOP_STATE_PATH = Path("runtime/trading_loop_state.json")


def get_new_york_now() -> datetime:
  return datetime.now(NEW_YORK_TIMEZONE)


def is_weekday(new_york_now: datetime) -> bool:
  return new_york_now.weekday() < 5


def read_trading_loop_state(
  path: Path = DEFAULT_TRADING_LOOP_STATE_PATH,
) -> dict:
  if not path.exists():
    return {}

  return json.loads(path.read_text(encoding="utf-8"))


def write_trading_loop_state(
  state: dict,
  path: Path = DEFAULT_TRADING_LOOP_STATE_PATH,
) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(state, indent=2, sort_keys=True),
    encoding="utf-8",
  )


def get_job_key(
  job_name: str,
  new_york_now: datetime,
) -> str:
  return f"{job_name}:{new_york_now.date().isoformat()}"


def has_job_run_today(
  job_name: str,
  new_york_now: datetime,
  path: Path = DEFAULT_TRADING_LOOP_STATE_PATH,
) -> bool:
  state = read_trading_loop_state(path)
  job_key = get_job_key(job_name, new_york_now)

  return state.get(job_key) == "completed"


def mark_job_run_today(
  job_name: str,
  new_york_now: datetime,
  path: Path = DEFAULT_TRADING_LOOP_STATE_PATH,
) -> None:
  state = read_trading_loop_state(path)
  job_key = get_job_key(job_name, new_york_now)

  state[job_key] = "completed"

  write_trading_loop_state(
    state=state,
    path=path,
  )


def should_run_daily_job(
  job_name: str,
  scheduled_time: time,
  new_york_now: datetime,
  path: Path = DEFAULT_TRADING_LOOP_STATE_PATH,
) -> bool:
  if not is_weekday(new_york_now):
    return False

  if new_york_now.time() < scheduled_time:
    return False

  return not has_job_run_today(
    job_name=job_name,
    new_york_now=new_york_now,
    path=path,
  )