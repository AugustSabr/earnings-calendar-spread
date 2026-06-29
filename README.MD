# Earnings Calendar Spreads

A small Python project for rebuilding an earnings options calendar-spread screener.

## Project structure

```text
src/earnings_calendar_spreads/
  core/       Pure logic and calculations.
              Should not depend on APIs, brokers, files, or UI.

  data/       Code for getting external data.
              Example: earnings calendars, stock prices, option chains.

  brokers/    Code for broker integrations.
              Example: IBKR order placement and position handling.

  workflow/   Code that connects the pieces together.
              Example: run a scan, screen symbols, place trades.
              
tests/        Small tests for the logic.
```

## Possible future improvements

- Add persistent logging of screening results, attempted orders, fills, and exits.
- Consider splitting the workflow into two steps if broker/order handling becomes slow:
  - pre-screen candidates 30–45 minutes before market close
  - re-check quotes and place orders about 15 minutes before close