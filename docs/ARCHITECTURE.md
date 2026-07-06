# Architecture

This project is split into small modules with clear boundaries.

## core/

Pure strategy logic and calculations.

Code in `core/` should not call external APIs, read files, place orders, or depend on live market connections.

Examples:

```text
symbol validation
earnings filtering
option expiration filtering
screening metrics
term structure
realized volatility
calendar spread pricing
position sizing
```

## data/

External data adapters.

Code in `data/` talks to public/data APIs and converts responses into formats used by `core/`.

Current examples:

```text
Finnhub earnings calendar
yfinance price history
yfinance option chains
```

## brokers/

Broker integrations.

Code in `brokers/` contains IBKR/TWS-specific behavior.

Examples:

```text
connect to IBKR/TWS
resolve stock and option contracts
fetch option chain parameters
read bid/ask quotes
build BAG/combo contracts
create entry/exit orders
read positions
identify open calendar spreads
```


## workflow/

Orchestration.

Code in `workflow/` connects data, core logic, broker logic, storage, and policies into useful flows.

Examples:

```text
scan earnings candidates
screen symbols
prepare a calendar entry
execute a calendar entry
prepare a calendar exit
execute a calendar exit
reconcile positions after order attempts
pause/resume trading checks
```

## notifications/

Telegram and notification formatting.

Current Telegram commands:

```text
/log [days]
/positions
/status
/pause
/resume
```


## storage/

Local runtime storage helpers.

Current storage:

```text
runtime/trade_log.jsonl
```

The trade log uses JSON Lines. Each event has:

```text
event_id
timestamp
event_type
trade_id
symbol
data
```

`trade_id` links open and close events for the same calendar spread.

## scripts/

Manual helper and runner scripts.

Scripts are used for inspection, manual testing, and running workflows during development. They are not unit tests.

Scripts may connect to external APIs, TWS, or Telegram.
