from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class EarningsEvent:
  """
  Representerer én earnings-hendelse for ett selskap.
  """
  symbol: str
  report_date: date
  report_time: str | None = None