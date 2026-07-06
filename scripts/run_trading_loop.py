import logging
import os
import time
import traceback
from datetime import time as clock_time

from dotenv import load_dotenv

from earnings_calendar_spreads.workflow.app_logging import (
  configure_app_logging,
)
from earnings_calendar_spreads.workflow.trading_loop_state import (
  get_new_york_now,
  mark_job_run_today,
  should_run_daily_job,
)


LOGGER = logging.getLogger(__name__)

EXIT_TIME = clock_time(9, 45)
ENTRY_TIME = clock_time(15, 45)


def get_loop_sleep_seconds() -> int:
  return int(os.getenv("TRADING_LOOP_SLEEP_SECONDS", "60"))


def should_force_crash() -> bool:
  return os.getenv("TRADING_LOOP_FORCE_CRASH", "0") == "1"


def run_exit_job(new_york_now) -> None:
  LOGGER.info("Would run calendar exit job.")
  mark_job_run_today(
    job_name="exit",
    new_york_now=new_york_now,
  )


def run_entry_job(new_york_now) -> None:
  LOGGER.info("Would run calendar entry job.")
  mark_job_run_today(
    job_name="entry",
    new_york_now=new_york_now,
  )


def run_loop_once() -> None:
  new_york_now = get_new_york_now()

  LOGGER.info("Trading loop heartbeat. new_york_time=%s", new_york_now)

  if should_force_crash():
    raise RuntimeError("Forced trading loop crash for testing.")

  if should_run_daily_job(
    job_name="exit",
    scheduled_time=EXIT_TIME,
    new_york_now=new_york_now,
  ):
    run_exit_job(new_york_now)

  if should_run_daily_job(
    job_name="entry",
    scheduled_time=ENTRY_TIME,
    new_york_now=new_york_now,
  ):
    run_entry_job(new_york_now)


def main():
  load_dotenv()
  configure_app_logging()

  sleep_seconds = get_loop_sleep_seconds()

  LOGGER.info("Trading loop started. sleep_seconds=%s", sleep_seconds)

  try:
    while True:
      try:
        run_loop_once()
      except Exception:
        LOGGER.error(
          "Trading loop iteration failed:\n%s",
          traceback.format_exc(),
        )

      time.sleep(sleep_seconds)

  except KeyboardInterrupt:
    LOGGER.info("Trading loop stopped by user.")


if __name__ == "__main__":
  main()