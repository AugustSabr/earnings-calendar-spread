# Implementation Notes

This file records practical implementation choices and edge cases that are easy to forget later.

## Data sources

Current split:

```text
yfinance = screening, estimates, quick market/option data
IBKR     = final source of truth before execution
```

Before trading, IBKR is used for option chains, listed strikes, contract resolution, conIds, quotes, orders, and positions.

## Expiration selection

Current rule:

```text
Short leg:
  first listed expiration on or after the earnings event

Long leg:
  first listed expiration on or after entry_date + 45 days
```

If the exact target long expiration is not listed, choose the first listed expiration after the target date.

Example:

```text
Entry date:        2026-07-01
Target long date:  2026-08-15
Selected expiry:   2026-08-21
```

## Strike selection

The intended strike is ATM, but both calendar legs must use the same listed strike.

IBKR may return a global strike list where not every strike exists for every expiration. Because of this, strike selection must use the intersection of strikes available for both the short and long expiration.

Current rule:

```text
1. Get strikes for short expiration.
2. Get strikes for long expiration.
3. Find common strikes.
4. Choose the common strike closest to the underlying price.
```

## Pricing

Entry uses natural debit:

```text
entry_debit = long_ask - short_bid
```

Close uses natural credit:

```text
close_credit = long_bid - short_ask
```

Prices are rounded to cents after calculation.

This is conservative and more fill-oriented than using mid price.

Possible later improvements:

```text
mid-price attempts
repricing
max slippage
more explicit liquidity rules
```

## Position sizing

Sizing currently supports a fixed dollar budget per symbol.

```text
estimated_total_debit = quoted_debit * 100 * quantity
quantity = floor(max_debit_per_symbol_usd / (quoted_debit * 100))
```

If the budget is too small for one spread, the trade should be skipped or fail clearly.

There is also a helper for percentage-based sizing:

```text
budget_per_symbol = account_value_snapshot_usd * risk_fraction
```

When account-based sizing is added to the real entry runner, account value should be snapshotted once at the start of the entry window. All candidates in the same run should use the same budget so order sizes do not depend on execution order.

## Order behavior

Entry and exit should not behave the same.

Entry:

```text
If not filled quickly, cancel and skip.
Better to miss a trade than enter badly.
```

Exit:

```text
If not filled quickly, cancel, re-read positions, and retry more aggressively.
Better to accept a worse exit than remain in an unwanted position.
```

Timeouts and retry rules should eventually become explicit policy values instead of being hardcoded in scripts.

## Partial fills and reconciliation

Partial fills can happen when order quantity is greater than one.

Example:

```text
Order quantity: 7
Filled:         3
Remaining:      4
```

After an order attempt, especially exit, the system should re-read positions and use actual remaining positions as truth.

Matched calendar quantity is:

```text
min(abs(short_position), long_position)
```

Entry and exit logging should not rely only on order status. If IBKR order status is delayed or unclear, positions are re-read and used as the source of truth.

## Trade logging

Trade events are written to:

```text
runtime/trade_log.jsonl
```

The file is JSON Lines, with one event per line.

Important event types:

```text
calendar_opened
calendar_closed
```

`trade_id` links the open and close event for the same calendar spread:

```text
SYMBOL|SHORT_EXPIRATION|LONG_EXPIRATION|STRIKE|RIGHT
```

`event_id` is unique per log line and is used for debugging/dedup/reference, not for matching open and close.

Current manual `check_ibkr_calendar_order.py` logs opened trades after confirmed fills. The qualified entry runner should use the same logging path before relying on unattended `--transmit` runs.

## Pause flag

Telegram `/pause` creates:

```text
runtime/trading_paused.flag
```

Telegram `/resume` removes it.

The qualified entry runner checks this flag and skips new entries while paused.

Pause means:

```text
do not open new positions
```

It should not prevent exits, because exits reduce risk.

## Market data

IBKR option bid/ask data is required for entry and exit pricing.

Contract lookup and option chain lookup can work outside regular market hours, but option bid/ask quotes may be unavailable when the US options market is closed.

If option quote scripts return no bid/ask for several liquid contracts, first check market hours and TWS market data status before changing code.
