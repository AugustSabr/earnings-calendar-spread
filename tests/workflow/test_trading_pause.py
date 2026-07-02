from earnings_calendar_spreads.workflow.trading_pause import (
  is_trading_paused,
  pause_trading,
  resume_trading,
)


def test_pause_and_resume_trading(tmp_path):
  path = tmp_path / "trading_paused.flag"

  assert is_trading_paused(path) is False

  pause_trading(path)

  assert is_trading_paused(path) is True
  assert path.read_text(encoding="utf-8") == "paused\n"

  resume_trading(path)

  assert is_trading_paused(path) is False


def test_resume_trading_when_not_paused(tmp_path):
  path = tmp_path / "trading_paused.flag"

  resume_trading(path)

  assert is_trading_paused(path) is False