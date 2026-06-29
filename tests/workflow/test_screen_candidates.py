from datetime import date

from earnings_calendar_spreads.core.models import ScreeningResult
from earnings_calendar_spreads.workflow import screen_candidates


def test_screen_earnings_candidates(monkeypatch):
  def fake_scan_earnings_candidates(today):
    return ["AAPL", "MSFT"]

  def fake_screen_symbol(symbol, today):
    return ScreeningResult(
      symbol=symbol,
      average_volume=2_000_000,
      iv30_rv30=1.40,
      term_structure_slope=-0.005,
      expected_move="5.2%",
      passes_average_volume=True,
      passes_iv30_rv30=True,
      passes_term_structure_slope=True,
      qualifies=True,
    )

  monkeypatch.setattr(
    screen_candidates,
    "scan_earnings_candidates",
    fake_scan_earnings_candidates,
  )
  monkeypatch.setattr(
    screen_candidates,
    "screen_symbol",
    fake_screen_symbol,
  )

  result = screen_candidates.screen_earnings_candidates(
    today=date(2026, 6, 29),
  )

  assert [item.symbol for item in result] == ["AAPL", "MSFT"]
  assert all(item.qualifies for item in result)


def test_screen_earnings_candidates_skips_symbols_with_errors(monkeypatch):
  def fake_scan_earnings_candidates(today):
    return ["AAPL", "BAD"]

  def fake_screen_symbol(symbol, today):
    if symbol == "BAD":
      raise ValueError("No options found.")

    return ScreeningResult(
      symbol=symbol,
      average_volume=2_000_000,
      iv30_rv30=1.40,
      term_structure_slope=-0.005,
      expected_move="5.2%",
      passes_average_volume=True,
      passes_iv30_rv30=True,
      passes_term_structure_slope=True,
      qualifies=True,
    )

  monkeypatch.setattr(
    screen_candidates,
    "scan_earnings_candidates",
    fake_scan_earnings_candidates,
  )
  monkeypatch.setattr(
    screen_candidates,
    "screen_symbol",
    fake_screen_symbol,
  )

  result = screen_candidates.screen_earnings_candidates(
    today=date(2026, 6, 29),
  )

  assert [item.symbol for item in result] == ["AAPL"]