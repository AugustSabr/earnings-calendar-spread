# Strategy

## Goal

This project screens for earnings-related options calendar spread trades.

The strategy looks for stocks with upcoming earnings where options pricing shows:

```text
enough stock liquidity
elevated implied volatility compared to realized volatility
inverted implied volatility term structure
a clear earnings-related options setup
```

The goal is not to predict earnings direction. The trade is based on volatility, timing, and option structure around the earnings event.

## Trade timing

The intended timing is a core part of the strategy:

```text
Enter about 15 minutes before market close before the earnings event.
Exit about 15 minutes after market open on the next trading day.
```

For after-market-close earnings, the trade is entered near the close on the earnings date.

For before-market-open earnings, the trade is entered near the close on the previous trading day.

## Candidate selection

The project scans the earnings calendar for:

```text
companies reporting after market close today
companies reporting before market open tomorrow
```

Symbols are filtered to keep only standard US stock tickers.

## Screening rules

A symbol qualifies only if all three filters pass:

```text
average_volume >= 1,500,000
iv30_rv30 >= 1.25
ts_slope_0_45 <= -0.00406
```

If any filter fails, the symbol is rejected.

## Average volume

Average volume is calculated from recent price history using a 30-period rolling average.

This avoids illiquid stocks where options fills and exits may be poor.

## IV30/RV30

IV30/RV30 compares estimated 30-day implied volatility with recent realized volatility.

```text
iv30_rv30 = IV at 30 DTE / 30-day realized volatility
```

Realized volatility is calculated with the Yang-Zhang volatility estimator.

Current threshold:

```text
iv30_rv30 >= 1.25
```

## Term structure

The system estimates implied volatility across option expirations.

For each expiration, it finds the strike closest to the current stock price and averages the ATM call IV and ATM put IV.

The term structure slope is calculated from the first available expiration to 45 DTE:

```text
ts_slope_0_45 = (IV at 45 DTE - IV at first expiry DTE) / (45 - first expiry DTE)
```

Current threshold:

```text
ts_slope_0_45 <= -0.00406
```

A negative slope means near-term implied volatility is higher than longer-term implied volatility, which is common around earnings.

## Expected move

Expected move is estimated from the front ATM straddle:

```text
expected_move = (ATM call mid + ATM put mid) / underlying price
```

Expected move is currently informational. It helps show how much movement the market is pricing in, but it is not a pass/fail rule.

## Intended trade

The intended trade is a long calendar spread:

```text
SELL front expiry option
BUY later expiry option
same symbol
same strike
same option right
same multiplier
```

The first version focuses on call calendars.

## Expiration and strike selection

The short leg uses the nearest relevant expiration on or after the earnings event.

The long leg uses a later expiration around 45 DTE, or the first available expiration beyond 45 DTE.

The strike should be ATM, meaning the common listed strike closest to the current stock price.

Both legs must use the same strike and standard 100-share option multiplier.

## Pricing

Entry uses natural debit:

```text
entry_debit = back_ask - front_bid
```

Close uses natural credit:

```text
close_credit = back_bid - front_ask
```

This is conservative. It is designed to avoid assuming fills at mid price.

## Position sizing

Calendar spreads are priced as option quotes, but the actual cash debit is usually:

```text
quoted spread debit * 100 * quantity
```

This is because standard US equity option contracts normally represent 100 shares.

Example:

```text
quoted calendar debit = 10.50
quantity = 1
cash debit = 10.50 * 100 = $1,050
```

Current implemented sizing supports a fixed dollar cap per symbol, for example:

```text
--max-debit=2500
```

The system then chooses the largest quantity that stays below that cap.

The later account-based idea is to cap each trade at a fixed percentage of account value, for example 7%. This is only a placeholder and should be adjusted after paper testing.

When a percentage rule is added, account value should be snapshotted once at the start of the entry window. All candidates in that run should use the same per-symbol budget so sizing does not depend on which order fills first.

A practical implication is that the account needs to be large enough for one spread to fit inside the per-trade budget. Many liquid large-cap calendar spreads may cost roughly $800-$2,500 per spread, but some can be much higher. With a 7% placeholder rule, an account around $20k-$30k is likely the minimum range where the strategy starts to work normally without frequently rounding position size down to zero.

## Broker execution

Broker execution currently uses IBKR Paper.

Current execution flow:

```text
resolve stock contract
get underlying price from IBKR
resolve option chain and listed strikes from IBKR
choose common ATM strike
resolve standard short option contract
resolve standard long option contract
get bid/ask quotes
build BAG/combo contract
submit limit order
track order status
re-read positions for reconciliation
write trade log event after confirmed fill
close position after next market open
```

## Current project status

Implemented and paper-tested:

```text
earnings scan
candidate filtering
yfinance screening data
average volume
Yang-Zhang realized volatility
IV30/RV30
term structure
expected move
qualified candidate workflow
IBKR contract resolution
IBKR option quote inspection
calendar spread planning
BAG/combo construction
entry order creation
paper entry transmit
exit prepare
paper exit transmit
position reconciliation
trade logging
trade log inspection
Telegram log/status/pause/resume/positions
pause flag for new entries
```

Still not final:

```text
production scheduling
account-value based sizing
final entry/exit retry policy
unattended qualified-entry logging path
live trading
```
