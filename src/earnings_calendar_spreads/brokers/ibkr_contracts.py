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

def make_option_contract(
  symbol: str,
  expiration: str,
  strike: float,
  right: str,
  exchange: str = "SMART",
) -> Contract:
  """
  Lager en enkel OPT-kontrakt for amerikansk aksjeopsjon.

  expiration forventes som YYYYMMDD.
  right forventes som C eller P.
  """
  contract = Contract()
  contract.symbol = symbol.strip().upper()
  contract.secType = "OPT"
  contract.exchange = exchange
  contract.currency = "USD"
  contract.lastTradeDateOrContractMonth = expiration
  contract.strike = float(strike)
  contract.right = right.strip().upper()
  contract.multiplier = "100"

  return contract