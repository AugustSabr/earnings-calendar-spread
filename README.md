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
  - Consider async or parallel candidate evaluation if screening becomes too slow near market close.

## IBKR API setup

This project uses the official IBKR TWS API Python client.

Do not install `ibapi` from PyPI. The PyPI package may be outdated and can cause order submission errors such as:

```text
IBKR error 10268: The 'EtradeOnly' order attribute is not supported.
```

Instead, install the Python API from the official TWS API package:
https://interactivebrokers.github.io/#

Install it into the active virtual environment:

```powershell
python -m pip uninstall ibapi
cd "C:\TWS API\source\pythonclient"
python -m pip install .
```

The project also requires TWS or IB Gateway to be running with API access enabled.

## Local development

Open PowerShell in the project folder:

```powershell
.venv\Scripts\Activate.ps1
```
