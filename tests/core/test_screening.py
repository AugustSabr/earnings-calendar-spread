from earnings_calendar_spreads.core.screening import create_screening_result

def test_creates_passing_screening_result():
  result = create_screening_result(
    symbol="aapl",
    average_volume=2_000_000,
    iv30_rv30=1.40,
    term_structure_slope=-0.005,
    expected_move="5.2%",
  )

  assert result.symbol == "AAPL"
  assert result.passes_average_volume
  assert result.passes_iv30_rv30
  assert result.passes_term_structure_slope
  assert result.qualifies

def test_creates_failing_screening_result():
  result = create_screening_result(
    symbol="AAPL",
    average_volume=2_000_000,
    iv30_rv30=1.10,
    term_structure_slope=-0.005,
    expected_move="5.2%",
  )

  assert result.passes_average_volume
  assert not result.passes_iv30_rv30
  assert result.passes_term_structure_slope
  assert not result.qualifies