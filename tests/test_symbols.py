from earnings_calendar_spreads.core.symbols import is_standard_us_symbol

def test_accepts_normal_symbols():
  assert is_standard_us_symbol("AAPL")
  assert is_standard_us_symbol("MSFT")
  assert is_standard_us_symbol("NVDA")

def test_rejects_empty_symbol():
  assert not is_standard_us_symbol("")
  assert not is_standard_us_symbol("   ")

def test_rejects_long_symbols():
  assert not is_standard_us_symbol("VERYLONG")

def test_rejects_symbols_with_special_characters():
  assert not is_standard_us_symbol("BRK.B")
  assert not is_standard_us_symbol("ABC-DEF")
  assert not is_standard_us_symbol("ABC/DEF")

def test_lowercase_is_ok():
  assert is_standard_us_symbol("aapl")