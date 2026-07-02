from dataclasses import replace
from math import floor

from earnings_calendar_spreads.core.models import CalendarSpreadPlan


OPTION_CONTRACT_MULTIPLIER = 100


def calculate_calendar_spread_debit_usd(
  quoted_debit: float,
  quantity: int = 1,
  multiplier: int = OPTION_CONTRACT_MULTIPLIER,
) -> float:
  if quoted_debit <= 0:
    raise ValueError("quoted_debit must be positive.")

  if quantity <= 0:
    raise ValueError("quantity must be positive.")

  if multiplier <= 0:
    raise ValueError("multiplier must be positive.")

  return quoted_debit * multiplier * quantity


def calculate_calendar_quantity_for_budget(
  max_debit_per_symbol_usd: float,
  quoted_debit: float,
  multiplier: int = OPTION_CONTRACT_MULTIPLIER,
) -> int:
  if max_debit_per_symbol_usd <= 0:
    raise ValueError("max_debit_per_symbol_usd must be positive.")

  if quoted_debit <= 0:
    raise ValueError("quoted_debit must be positive.")

  if multiplier <= 0:
    raise ValueError("multiplier must be positive.")

  debit_per_spread = quoted_debit * multiplier

  return floor(max_debit_per_symbol_usd / debit_per_spread)


def apply_budget_to_calendar_plan(
  plan: CalendarSpreadPlan,
  max_debit_per_symbol_usd: float,
  multiplier: int = OPTION_CONTRACT_MULTIPLIER,
) -> CalendarSpreadPlan:
  if plan.net_debit is None:
    raise ValueError("plan.net_debit is required before sizing.")

  quantity = calculate_calendar_quantity_for_budget(
    max_debit_per_symbol_usd=max_debit_per_symbol_usd,
    quoted_debit=plan.net_debit,
    multiplier=multiplier,
  )

  if quantity <= 0:
    raise ValueError(
      "max_debit_per_symbol_usd is too small for one calendar spread."
    )

  return replace(
    plan,
    quantity=quantity,
  )