# Earnings Calendar Spreads

A Python project for screening earnings-related options calendar spreads and testing the full entry/exit workflow in IBKR Paper.

## Project structure

```text
src/earnings_calendar_spreads/
  core/          Pure strategy logic and calculations.
  data/          External data adapters such as Finnhub and yfinance.
  brokers/       IBKR/TWS contracts, market data, orders, and positions.
  workflow/      Orchestration across core, data, broker, and storage code.
  notifications/ Telegram formatting and bot helpers.
  storage/       Runtime trade-log helpers.

scripts/         Manual development and operational scripts.
tests/           Unit tests.
runtime/         Local runtime files. Not committed.
```

## Setup on a new PC

Clone or pull the repo, then create a local virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

The virtual environment is local to each PC and should not be committed.

## IBKR API setup

This project uses the official IBKR TWS API Python client.

Do not install `ibapi` from PyPI. The PyPI package can be outdated and may cause compatibility issues with newer TWS/API versions.

Install the Python API from the official TWS API package into the active virtual environment:

```powershell
python -m pip uninstall ibapi
pip install "...\TWS API\source\pythonclient"
```

Then verify:

```powershell
python -c "import ibapi; print(ibapi.__file__)"
```

TWS or IB Gateway must be running with API access enabled. For Paper Trading the default socket port is usually `7497`.

## Environment variables

Create `.env` from `.env.example`:

```text
FINNHUB_API_KEY=...
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=180
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Required services:

```text
Finnhub   = earnings calendar
yfinance  = screening data
IBKR/TWS  = final option chains, quotes, orders, and positions
Telegram  = optional bot/status notifications
```

## Local checks

Run unit tests:

```powershell
pytest
```

Check IBKR connectivity:

```powershell
python scripts/check_ibkr_connection.py
```

Check an option quote during US option market hours:

```powershell
python scripts/check_ibkr_option_quote.py AAPL 20260710 310 C
```

## Common scripts

### Entry preview / paper entry

```powershell
python scripts/check_ibkr_calendar_order.py AAPL 2026-07-10
python scripts/check_ibkr_calendar_order.py AAPL 2026-07-10 --max-debit=2500
python scripts/check_ibkr_calendar_order.py AAPL 2026-07-10 --max-debit=2500 --transmit
```

Notes:

```text
Default mode submits an untransmitted/staged order to TWS.
--max-debit=2500 sizes the quantity so estimated debit stays below $2,500.
--transmit sends the order to IBKR Paper.
```

### Qualified entry runner

```powershell
python scripts/run_qualified_calendar_entries.py
python scripts/run_qualified_calendar_entries.py --stage
python scripts/run_qualified_calendar_entries.py --transmit
```

Modes:

```text
default   prepare qualified candidates only
--stage   stage untransmitted orders in TWS
--transmit send orders to IBKR Paper
```

This runner respects `runtime/trading_paused.flag` and skips new entries while trading is paused.

### Exit runner

```powershell
python scripts/run_calendar_exits.py
python scripts/run_calendar_exits.py --prepare
python scripts/run_calendar_exits.py --stage
python scripts/run_calendar_exits.py --transmit
python scripts/run_calendar_exits.py AAPL MSFT --prepare
```

Modes:

```text
default   list detected open calendar spreads
--prepare price close orders without placing orders
--stage   stage untransmitted close orders in TWS
--transmit send close orders to IBKR Paper
```

The exit workflow re-reads IBKR positions and uses positions as the source of truth.

### Position and log inspection

```powershell
python scripts/check_ibkr_calendar_positions.py
python scripts/check_trade_log.py
```

`check_ibkr_calendar_positions.py` reads actual IBKR positions.

`check_trade_log.py` summarizes local events from `runtime/trade_log.jsonl`.

### Telegram bot

```powershell
python scripts/run_telegram_bot.py
```

Supported commands:

```text
/log [days] - show trade-log events from the last N days, default 1.
/positions  - show open calendar spreads from IBKR.
/status     - show pause status and open logged trades.
/pause      - pause new entries.
/resume     - allow new entries again.
```

The bot sends short online/offline messages. `/positions` connects to IBKR on demand; `/log`, `/status`, `/pause`, and `/resume` do not need market data.

Stop the bot from the terminal with:

```text
q
```

## Runtime files

Runtime files live under `runtime/` and are ignored by git.

```text
runtime/trade_log.jsonl       local JSON Lines trade event log
runtime/trading_paused.flag   pause flag used to skip new entries
```

`trade_log.jsonl` is JSON Lines: one JSON object per line. This is intentional because it is safe and simple to append to.

Readable summary:

```powershell
python scripts/check_trade_log.py
```

Pretty-print raw JSON Lines in PowerShell:

```powershell
Get-Content runtime/trade_log.jsonl | ForEach-Object { $_ | ConvertFrom-Json | ConvertTo-Json -Depth 20 }
```
