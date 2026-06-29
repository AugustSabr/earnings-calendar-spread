import pytest

from earnings_calendar_spreads.core.screening_metrics import calculate_iv30_rv30


def test_calculates_iv30_rv30():
  def fake_term_structure(dte: int) -> float:
    return 0.50

  result = calculate_iv30_rv30(
    term_structure=fake_term_structure,
    realized_volatility_30=0.25,
  )

  assert result == 2.0


def test_raises_error_when_realized_volatility_is_zero():
  def fake_term_structure(dte: int) -> float:
    return 0.50

  with pytest.raises(ValueError):
    calculate_iv30_rv30(
      term_structure=fake_term_structure,
      realized_volatility_30=0.0,
    )