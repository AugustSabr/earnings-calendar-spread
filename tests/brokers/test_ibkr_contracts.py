from earnings_calendar_spreads.brokers.ibkr_contracts import make_stock_contract


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