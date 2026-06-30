from dataclasses import dataclass


@dataclass(frozen=True)
class EntryOrderPolicy:
  """
  Policy for entry-orders.

  Første versjon:
  - vent kort på fill
  - cancel hvis ikke fylt
  - ingen retry
  """
  fill_timeout_seconds: int = 30
  cancel_if_not_filled: bool = True
  retry: bool = False


@dataclass(frozen=True)
class ExitOrderPolicy:
  """
  Policy for exit-orders.

  Første versjon:
  - exit er viktigere enn entry
  - kan retryes senere med mer aggressiv pris
  """
  fill_timeout_seconds: int = 30
  cancel_if_not_filled: bool = True
  retry: bool = True
  max_retries: int = 0
  price_adjustment: float = 0.0