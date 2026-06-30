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

@dataclass(frozen=True)
class ScreeningResult:
  """
  Resultat fra options/volatility-screening for ett symbol.
  """
  symbol: str
  average_volume: float
  iv30_rv30: float
  term_structure_slope: float
  expected_move: str | None
  passes_average_volume: bool
  passes_iv30_rv30: bool
  passes_term_structure_slope: bool
  qualifies: bool

@dataclass(frozen=True)
class CalendarSpreadPlan:
  """
  Broker-uavhengig plan for en calendar spread.
  """
  symbol: str
  short_expiration: str
  long_expiration: str
  strike: float
  right: str
  quantity: int
  net_debit: float