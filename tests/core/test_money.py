from earnings_calendar_spreads.core.money import format_usd


def test_format_usd():
  assert format_usd(1234.5) == "$1,234.50"