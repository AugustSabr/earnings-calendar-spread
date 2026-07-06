import pytest

from earnings_calendar_spreads.brokers.ibkr_positions import (
  get_positions_with_retry,
)


class FakePositionsClient:
  def __init__(self, failures_before_success, positions):
    self.failures_before_success = failures_before_success
    self.positions = positions
    self.calls = 0

  def get_positions(self):
    self.calls += 1

    if self.calls <= self.failures_before_success:
      raise TimeoutError("Timed out waiting for IBKR positions.")

    return self.positions


def test_get_positions_with_retry_returns_positions():
  client = FakePositionsClient(
    failures_before_success=0,
    positions=["position"],
  )

  assert get_positions_with_retry(
    client=client,
    delay_seconds=0,
  ) == ["position"]

  assert client.calls == 1


def test_get_positions_with_retry_retries_timeout():
  client = FakePositionsClient(
    failures_before_success=1,
    positions=["position"],
  )

  assert get_positions_with_retry(
    client=client,
    attempts=3,
    delay_seconds=0,
  ) == ["position"]

  assert client.calls == 2


def test_get_positions_with_retry_raises_after_attempts():
  client = FakePositionsClient(
    failures_before_success=3,
    positions=["position"],
  )

  with pytest.raises(TimeoutError):
    get_positions_with_retry(
      client=client,
      attempts=2,
      delay_seconds=0,
    )

  assert client.calls == 2


def test_get_positions_with_retry_rejects_invalid_attempts():
  client = FakePositionsClient(
    failures_before_success=0,
    positions=[],
  )

  with pytest.raises(ValueError, match="attempts"):
    get_positions_with_retry(
      client=client,
      attempts=0,
      delay_seconds=0,
    )