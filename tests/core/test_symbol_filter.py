from earnings_calendar_spreads.core.symbol_filter import filter_standard_symbols


def test_filters_and_normalizes_symbols():
  symbols = ["aapl", "MSFT", "BRK.B", "", " verylong ", "nvda"]

  result = filter_standard_symbols(symbols)

  assert result == ["AAPL", "MSFT", "NVDA"]