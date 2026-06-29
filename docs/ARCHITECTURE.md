# Architecture

This project is split into four main areas.

## core/

Pure strategy logic.

Code in `core/` should not call external APIs, read files, place orders, or depend on live market connections.

Examples:
- symbol validation
- earnings filtering
- option expiration filtering
- ATM IV calculations
- term structure
- realized volatility
- screening rules

## data/

External data adapters.

Code in `data/` talks to APIs such as Finnhub and yfinance, then converts the response into formats used by `core/`.

Examples:
- Finnhub earnings calendar
- yfinance price history
- yfinance option chains

## workflow/

Orchestration.

Code in `workflow/` connects data adapters and core logic into useful flows.

Examples:
- scan earnings candidates
- screen one symbol
- screen all earnings candidates

## brokers/

Broker integrations.

Code in `brokers/` should contain order-related logic and broker API code.

Examples:
- connect to IBKR/TWS
- resolve contracts
- get option quotes
- place calendar spread orders
- close open positions

## scripts/

Manual helper scripts.

Scripts are used for inspecting data and manually running workflows during development.
They are not unit tests.

Examples:
- check Finnhub response format
- check yfinance option data
- run candidate screening