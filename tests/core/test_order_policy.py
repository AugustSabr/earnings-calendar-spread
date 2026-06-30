from earnings_calendar_spreads.core.order_policy import (
  EntryOrderPolicy,
  ExitOrderPolicy,
)


def test_default_entry_order_policy():
  policy = EntryOrderPolicy()

  assert policy.fill_timeout_seconds == 30
  assert policy.cancel_if_not_filled is True
  assert policy.retry is False


def test_default_exit_order_policy():
  policy = ExitOrderPolicy()

  assert policy.fill_timeout_seconds == 30
  assert policy.cancel_if_not_filled is True
  assert policy.retry is True
  assert policy.max_retries == 0
  assert policy.price_adjustment == 0.0


def test_custom_exit_order_policy():
  policy = ExitOrderPolicy(
    fill_timeout_seconds=10,
    max_retries=3,
    price_adjustment=0.05,
  )

  assert policy.fill_timeout_seconds == 10
  assert policy.max_retries == 3
  assert policy.price_adjustment == 0.05