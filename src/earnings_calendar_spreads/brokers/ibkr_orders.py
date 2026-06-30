from ibapi.order import Order


def build_calendar_spread_limit_order(
  net_debit: float,
  quantity: int = 1,
  transmit: bool = False,
) -> Order:
  """
  Bygger en limit order for long calendar spread.

  For long calendar:
  - BUY comboen
  - betal net debit
  """
  if quantity <= 0:
    raise ValueError("quantity must be greater than zero.")

  if net_debit <= 0:
    raise ValueError("net_debit must be greater than zero.")

  order = Order()
  order.action = "BUY"
  order.orderType = "LMT"
  order.totalQuantity = quantity
  order.lmtPrice = float(net_debit)
  order.tif = "DAY"
  order.transmit = transmit

  return order

def build_calendar_spread_close_order(
  close_credit: float,
  quantity: int = 1,
  transmit: bool = False,
) -> Order:
  """
  Bygger limit order for å lukke en long calendar spread.

  Brukes med samme BAG-contract som entry.
  SELL combo lukker:
  - short/front kjøpes tilbake
  - long/back selges
  """
  if quantity <= 0:
    raise ValueError("quantity must be greater than zero.")

  if close_credit <= 0:
    raise ValueError("close_credit must be greater than zero.")

  order = Order()
  order.action = "SELL"
  order.orderType = "LMT"
  order.totalQuantity = quantity
  order.lmtPrice = float(close_credit)
  order.tif = "DAY"
  order.transmit = transmit

  return order