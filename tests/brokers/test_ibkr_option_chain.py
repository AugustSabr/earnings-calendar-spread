import pytest

from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  IBKROptionChainParameters,
  ibkr_expiration_to_iso,
  iso_expiration_to_ibkr,
  select_option_chain_parameters,
)


def test_select_option_chain_parameters_prefers_smart():
  parameters = [
    IBKROptionChainParameters(
      exchange="CBOE",
      underlying_con_id=1,
      trading_class="AAPL",
      multiplier="100",
      expirations=["20260717"],
      strikes=[300.0],
    ),
    IBKROptionChainParameters(
      exchange="SMART",
      underlying_con_id=1,
      trading_class="AAPL",
      multiplier="100",
      expirations=["20260717"],
      strikes=[300.0],
    ),
  ]

  selected = select_option_chain_parameters(parameters)

  assert selected.exchange == "SMART"


def test_select_option_chain_parameters_requires_parameters():
  with pytest.raises(ValueError, match="parameters"):
    select_option_chain_parameters([])


def test_select_option_chain_parameters_requires_matching_exchange():
  parameters = [
    IBKROptionChainParameters(
      exchange="CBOE",
      underlying_con_id=1,
      trading_class="AAPL",
      multiplier="100",
      expirations=["20260717"],
      strikes=[300.0],
    ),
  ]

  with pytest.raises(ValueError, match="exchange=SMART"):
    select_option_chain_parameters(parameters)


def test_ibkr_expiration_to_iso():
  assert ibkr_expiration_to_iso("20260717") == "2026-07-17"


def test_iso_expiration_to_ibkr():
  assert iso_expiration_to_ibkr("2026-07-17") == "20260717"