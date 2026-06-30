from earnings_calendar_spreads.brokers.ibkr_contracts import (
  make_stock_contract,
  make_option_contract,
  make_option_expiration_query_contract,
)


def test_make_stock_contract():
  contract = make_stock_contract(
    symbol="aapl",
    primary_exchange="NASDAQ",
  )

  assert contract.symbol == "AAPL"
  assert contract.secType == "STK"
  assert contract.exchange == "SMART"
  assert contract.currency == "USD"
  assert contract.primaryExchange == "NASDAQ"


def test_make_stock_contract_without_primary_exchange():
  contract = make_stock_contract("MSFT")

  assert contract.symbol == "MSFT"
  assert contract.primaryExchange == ""

def test_make_option_contract():
  contract = make_option_contract(
    symbol="aapl",
    expiration="20260717",
    strike=100,
    right="c",
  )

  assert contract.symbol == "AAPL"
  assert contract.secType == "OPT"
  assert contract.exchange == ""
  assert contract.currency == "USD"
  assert contract.lastTradeDateOrContractMonth == "20260717"
  assert contract.strike == 100.0
  assert contract.right == "C"
  assert contract.multiplier == "100"

def test_make_option_contract_with_exchange():
  contract = make_option_contract(
    symbol="aapl",
    expiration="20260717",
    strike=300,
    right="c",
    exchange="SMART",
  )

  assert contract.exchange == "SMART"

def test_make_option_expiration_query_contract():
  contract = make_option_expiration_query_contract(
    symbol="aapl",
    expiration="20260821",
    right="c",
  )

  assert contract.symbol == "AAPL"
  assert contract.secType == "OPT"
  assert contract.currency == "USD"
  assert contract.lastTradeDateOrContractMonth == "20260821"
  assert contract.right == "C"
  assert contract.multiplier == "100"
  assert contract.exchange == ""