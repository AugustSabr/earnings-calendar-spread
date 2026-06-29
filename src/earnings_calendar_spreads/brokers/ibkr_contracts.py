from ibapi.contract import Contract


def make_stock_contract(
  symbol: str,
  primary_exchange: str | None = None,
) -> Contract:
  """
  Lager en enkel STK-kontrakt for amerikansk aksje.
  """
  contract = Contract()
  contract.symbol = symbol.strip().upper()
  contract.secType = "STK"
  contract.exchange = "SMART"
  contract.currency = "USD"

  if primary_exchange:
    contract.primaryExchange = primary_exchange

  return contract