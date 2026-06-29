from earnings_calendar_spreads.core.models import ScreeningResult
from earnings_calendar_spreads.core.screening_metrics import passes_average_volume_filter
from earnings_calendar_spreads.core.screening_metrics import passes_iv30_rv30_filter
from earnings_calendar_spreads.core.screening_metrics import passes_term_structure_slope_filter

def create_screening_result(
  symbol: str,
  average_volume: float,
  iv30_rv30: float,
  term_structure_slope: float,
  expected_move: str | None,
) -> ScreeningResult:
  """
  Lager et ScreeningResult-objekt fra ferdigberegnede metrikker.
  """
  passes_average_volume = passes_average_volume_filter(average_volume)
  passes_iv30_rv30 = passes_iv30_rv30_filter(iv30_rv30)
  passes_term_structure_slope = passes_term_structure_slope_filter(
    term_structure_slope,
  )

  qualifies = (
    passes_average_volume
    and passes_iv30_rv30
    and passes_term_structure_slope
  )

  return ScreeningResult(
    symbol=symbol.strip().upper(),
    average_volume=average_volume,
    iv30_rv30=iv30_rv30,
    term_structure_slope=term_structure_slope,
    expected_move=expected_move,
    passes_average_volume=passes_average_volume,
    passes_iv30_rv30=passes_iv30_rv30,
    passes_term_structure_slope=passes_term_structure_slope,
    qualifies=qualifies,
  )