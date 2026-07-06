import logging
import time
import traceback

from dotenv import load_dotenv

from earnings_calendar_spreads.workflow.app_logging import (
  configure_app_logging,
)


LOGGER = logging.getLogger(__name__)


def run_loop_once() -> None:
  LOGGER.info("Trading loop heartbeat.")


def main():
  load_dotenv()
  configure_app_logging()

  LOGGER.info("Trading loop started.")

  try:
    while True:
      try:
        run_loop_once()
      except Exception:
        LOGGER.error(
          "Trading loop iteration failed:\n%s",
          traceback.format_exc(),
        )

      time.sleep(60)

  except KeyboardInterrupt:
    LOGGER.info("Trading loop stopped by user.")


if __name__ == "__main__":
  main()