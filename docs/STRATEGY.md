# Strategy

## Goal

This project screens for earnings-related options calendar spread trades.

The strategy looks for stocks with upcoming earnings where options pricing shows:

* enough stock liquidity
* elevated implied volatility compared to realized volatility
* inverted implied volatility term structure
* a clear earnings-related options setup

The goal is not to predict earnings direction. The trade is based on volatility, timing, and option structure around the earnings event.

## Trade timing

The intended timing is a core part of the strategy:

* Enter about 15 minutes before market close before the earnings event.
* Exit about 15 minutes after market open on the next trading day.

For after-market-close earnings, the trade is entered near the close on the earnings date.

For before-market-open earnings, the trade is entered near the close on the previous trading day.

## Candidate selection

The project scans the earnings calendar for:

* companies reporting after market close today
* companies reporting before market open tomorrow

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

The current threshold is:

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

The current threshold is:

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

The short leg should use the nearest relevant expiration after the earnings event.

The long leg should use a later expiration around 45 DTE, or the first available expiration beyond 45 DTE.

The strike should be ATM, meaning the available option strike closest to the current stock price.

Both legs should use the same strike.

## Pricing

A long calendar spread is entered for a net debit.

```text
net_debit = back_ask - front_bid
```

The first automated version should use conservative limit orders.

## Broker execution

Broker execution starts with IBKR paper trading.

Planned execution flow:

```text
resolve stock contract
resolve short option contract
resolve long option contract
build BAG/combo contract
submit limit order
track fill
close position after next market open
```

## Current project status

Implemented:

* earnings scan
* candidate filtering
* yfinance price and options data
* average volume
* Yang-Zhang realized volatility
* IV30/RV30
* term structure
* expected move
* symbol screening
* candidate screening workflow
* IBKR connection check
* IBKR stock contract lookup
* IBKR option contract lookup
* IBKR option bid/ask inspection

Not yet implemented:

* calendar spread leg selection
* BAG/combo contract construction
* calendar spread order creation
* order submission
* fill tracking
* exit workflow
* persistent trade logging