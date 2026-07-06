import logging
from pathlib import Path


DEFAULT_APP_LOG_PATH = Path("runtime/app.log")


def configure_app_logging(
  path: Path = DEFAULT_APP_LOG_PATH,
) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
      logging.FileHandler(path, encoding="utf-8"),
      logging.StreamHandler(),
    ],
  )