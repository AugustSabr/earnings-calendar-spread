import logging
import os
import time
import traceback
from datetime import time as clock_time
import subprocess
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.workflow.app_logging import (
  configure_app_logging,
)
from earnings_calendar_spreads.workflow.trading_loop_state import (
  get_new_york_now,
  mark_job_run_today,
  should_run_daily_job,
)
from earnings_calendar_spreads.notifications.telegram import (
  TelegramConfig,
  send_telegram_message,
)


LOGGER = logging.getLogger(__name__)

EXIT_TIME = clock_time(9, 45)
ENTRY_TIME = clock_time(15, 45)

ERROR_NOTIFICATION_COOLDOWN_SECONDS = 300
MAX_TELEGRAM_MESSAGE_LENGTH = 3500

def get_loop_sleep_seconds() -> int:
  return int(os.getenv("TRADING_LOOP_SLEEP_SECONDS", "60"))


def should_force_crash() -> bool:
  return os.getenv("TRADING_LOOP_FORCE_CRASH", "0") == "1"


def run_exit_job(new_york_now) -> None:
  mode = get_trading_loop_exit_mode()
  command = [
    sys.executable,
    "scripts/run_calendar_exits.py",
  ]

  if mode != "prepare":
    command.append(f"--{mode}")
  else:
    command.append("--prepare")

  run_subprocess_job(
    command=command,
    job_name="exit",
  )

  mark_job_run_today(
    job_name="exit",
    new_york_now=new_york_now,
  )


def run_entry_job(new_york_now) -> None:
  mode = get_trading_loop_entry_mode()
  command = [
    sys.executable,
    "scripts/run_qualified_calendar_entries.py",
  ]

  if mode == "stage":
    command.append("--stage")

  if mode == "transmit":
    command.append("--transmit")

  run_subprocess_job(
    command=command,
    job_name="entry",
  )

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

def get_optional_env(name: str) -> str | None:
  value = os.getenv(name)

  if not value:
    return None

  return value


def get_telegram_config() -> TelegramConfig | None:
  bot_token = get_optional_env("TELEGRAM_BOT_TOKEN")
  chat_id = get_optional_env("TELEGRAM_CHAT_ID")

  if bot_token is None or chat_id is None:
    return None

  return TelegramConfig(
    bot_token=bot_token,
    chat_id=chat_id,
  )


def truncate_telegram_message(text: str) -> str:
  if len(text) <= MAX_TELEGRAM_MESSAGE_LENGTH:
    return text

  return text[:MAX_TELEGRAM_MESSAGE_LENGTH] + "\n\n... truncated"


def send_loop_notification(
  config: TelegramConfig | None,
  text: str,
) -> None:
  if config is None:
    return

  try:
    send_telegram_message(
      config=config,
      text=truncate_telegram_message(text),
    )
  except Exception as error:
    LOGGER.error("Failed to send Telegram notification: %s", error)

def get_job_timeout_seconds() -> int:
  return int(os.getenv("TRADING_LOOP_JOB_TIMEOUT_SECONDS", "1800"))


def run_subprocess_job(
  command: list[str],
  job_name: str,
) -> None:
  LOGGER.info("Starting %s job: %s", job_name, " ".join(command))

  result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    timeout=get_job_timeout_seconds(),
  )

  if result.stdout:
    LOGGER.info("%s stdout:\n%s", job_name, result.stdout)

  if result.stderr:
    LOGGER.warning("%s stderr:\n%s", job_name, result.stderr)

  if result.returncode != 0:
    raise RuntimeError(
      f"{job_name} job failed with exit code {result.returncode}"
    )

  LOGGER.info("%s job completed successfully.", job_name)

def get_trading_loop_entry_mode() -> str:
  mode = os.getenv("TRADING_LOOP_ENTRY_MODE", "prepare").lower()

  if mode not in {"prepare", "stage", "transmit"}:
    raise ValueError("TRADING_LOOP_ENTRY_MODE must be prepare, stage, or transmit.")

  return mode


def get_trading_loop_exit_mode() -> str:
  mode = os.getenv("TRADING_LOOP_EXIT_MODE", "prepare").lower()

  if mode not in {"prepare", "stage", "transmit"}:
    raise ValueError("TRADING_LOOP_EXIT_MODE must be prepare, stage, or transmit.")

  return mode

def main():
  load_dotenv()
  configure_app_logging()

  sleep_seconds = get_loop_sleep_seconds()

  telegram_config = get_telegram_config()
  last_error_notification_time = 0.0

  LOGGER.info("Trading loop started. sleep_seconds=%s", sleep_seconds)

  LOGGER.info(
    "Trading loop modes. entry_mode=%s exit_mode=%s",
    get_trading_loop_entry_mode(),
    get_trading_loop_exit_mode(),
  )

  send_loop_notification(
    config=telegram_config,
    text="Trading loop online.",
  )

  try:
    while True:
      try:
        run_loop_once()
      except Exception:
        error_traceback = traceback.format_exc()

        LOGGER.error(
          "Trading loop iteration failed:\n%s",
          error_traceback,
        )

        current_time = time.monotonic()

        if (
          current_time - last_error_notification_time
          >= ERROR_NOTIFICATION_COOLDOWN_SECONDS
        ):
          send_loop_notification(
            config=telegram_config,
            text=(
              "Trading loop iteration failed.\n\n"
              f"{error_traceback}"
            ),
          )
          last_error_notification_time = current_time

      time.sleep(sleep_seconds)

  except KeyboardInterrupt:
    LOGGER.info("Trading loop stopped by user.")

    send_loop_notification(
      config=telegram_config,
      text="Trading loop stopped by user.",
    )


if __name__ == "__main__":
  main()