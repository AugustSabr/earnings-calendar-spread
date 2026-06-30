def calculate_calendar_net_debit(
  front_bid: float,
  back_ask: float,
) -> float:
  """
  Beregner net debit for en long calendar spread.

  Long calendar:
  - selg front option på bid
  - kjøp back option på ask
  """
  if front_bid <= 0:
    raise ValueError("front_bid must be greater than zero.")

  if back_ask <= 0:
    raise ValueError("back_ask must be greater than zero.")

  net_debit = back_ask - front_bid

  if net_debit <= 0:
    raise ValueError("net_debit must be greater than zero.")

  return net_debit