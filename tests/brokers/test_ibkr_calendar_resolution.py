from dataclasses import dataclass

from ibapi.contract import Contract

from earnings_calendar_spreads.brokers.ibkr_calendar_resolution import (
  adjust_plan_to_common_strike,
)
from earnings_calendar_spreads.core.models import CalendarSpreadPlan


@dataclass
class FakeContractDetails:
  contract: Contract


class FakeClient:
  def get_contract_details(
    self,
    contract,
    timeout=20,
  ):
    if contract.lastTradeDateOrContractMonth == "20260701":
      return [
        make_fake_contract_details(280.0),
        make_fake_contract_details(282.5),
        make_fake_contract_details(285.0),
      ]

    if contract.lastTradeDateOrContractMonth == "20260821":
      return [
        make_fake_contract_details(275.0),
        make_fake_contract_details(280.0),
        make_fake_contract_details(285.0),
      ]

    return []


def make_fake_contract_details(strike: float):
  contract = Contract()
  contract.strike = strike

  return FakeContractDetails(
    contract=contract,
  )


def test_adjust_plan_to_common_strike():
  plan = CalendarSpreadPlan(
    symbol="AAPL",
    short_expiration="2026-07-01",
    long_expiration="2026-08-21",
    strike=282.5,
    right="C",
    quantity=1,
  )

  adjusted_plan = adjust_plan_to_common_strike(
    client=FakeClient(),
    plan=plan,
    underlying_price=281.74,
  )

  assert adjusted_plan.strike == 280.0
  assert adjusted_plan.short_expiration == "2026-07-01"
  assert adjusted_plan.long_expiration == "2026-08-21"