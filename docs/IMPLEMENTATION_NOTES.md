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

Example:

```text
Underlying price: 281.74

Short expiry has:
  280.0, 282.5, 285.0

Long expiry has:
  275.0, 280.0, 285.0

282.5 is closest, but only exists for the short expiry.
Choose the closest common strike instead.
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

This is conservative and more fill-oriented than using mid price.

Possible later improvements:

```text
mid-price attempts
repricing
max slippage
more explicit liquidity rules
```

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

Timeouts and retry rules are not final yet. They should become explicit policy values instead of being hardcoded in scripts.

## Partial fills

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

## Position sizing

Not implemented yet.

Eventually, quantity should be based on account size and max allocation per trade.

A possible value to investigate later:

```text
around 7% of total account value per trade
```

This is not confirmed and should not be treated as a final rule.