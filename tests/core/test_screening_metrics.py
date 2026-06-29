import pytest
import pandas as pd

from earnings_calendar_spreads.core.screening_metrics import calculate_iv30_rv30
from earnings_calendar_spreads.core.screening_metrics import calculate_average_volume
from earnings_calendar_spreads.core.screening_metrics import passes_average_volume_filter
from earnings_calendar_spreads.core.screening_metrics import passes_all_screening_filters
from earnings_calendar_spreads.core.screening_metrics import passes_iv30_rv30_filter
from earnings_calendar_spreads.core.screening_metrics import passes_term_structure_slope_filter

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

def test_calculates_average_volume():
  price_history = pd.DataFrame({
    "Volume": [1_000_000] * 29 + [2_000_000],
  })

  result = calculate_average_volume(price_history)

  expected = ((1_000_000 * 29) + 2_000_000) / 30

  assert result == expected

def test_average_volume_filter_passes_when_volume_is_high_enough():
  assert passes_average_volume_filter(1_500_000)
  assert passes_average_volume_filter(2_000_000)

def test_average_volume_filter_fails_when_volume_is_too_low():
  assert not passes_average_volume_filter(1_499_999)

def test_average_volume_raises_error_when_not_enough_data():
  price_history = pd.DataFrame({
    "Volume": [1_000_000] * 10,
  })

  with pytest.raises(ValueError):
    calculate_average_volume(price_history)

def test_iv30_rv30_filter_passes_when_ratio_is_high_enough():
  assert passes_iv30_rv30_filter(1.25)
  assert passes_iv30_rv30_filter(1.50)

def test_iv30_rv30_filter_fails_when_ratio_is_too_low():
  assert not passes_iv30_rv30_filter(1.24)

def test_term_structure_slope_filter_passes_when_slope_is_low_enough():
  assert passes_term_structure_slope_filter(-0.00406)
  assert passes_term_structure_slope_filter(-0.01)

def test_term_structure_slope_filter_fails_when_slope_is_too_high():
  assert not passes_term_structure_slope_filter(-0.003)

def test_passes_all_screening_filters():
  result = passes_all_screening_filters(
    average_volume=1_500_000,
    iv30_rv30=1.25,
    term_structure_slope=-0.00406,
  )

  assert result

def test_fails_all_screening_filters_if_one_filter_fails():
  result = passes_all_screening_filters(
    average_volume=1_500_000,
    iv30_rv30=1.24,
    term_structure_slope=-0.00406,
  )

  assert not result