from pathlib import Path


DEFAULT_TRADING_PAUSE_PATH = Path("runtime/trading_paused.flag")


def is_trading_paused(
  path: Path = DEFAULT_TRADING_PAUSE_PATH,
) -> bool:
  return path.exists()


def pause_trading(
  path: Path = DEFAULT_TRADING_PAUSE_PATH,
) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text("paused\n", encoding="utf-8")


def resume_trading(
  path: Path = DEFAULT_TRADING_PAUSE_PATH,
) -> None:
  if path.exists():
    path.unlink()