from datetime import date

from earnings_calendar_spreads.core.candidates import find_earnings_candidates
from earnings_calendar_spreads.data.finnhub_client import get_earnings_calendar
from earnings_calendar_spreads.data.finnhub_parser import parse_finnhub_earnings_events
from earnings_calendar_spreads.core.candidates import (
  find_earnings_candidate_events,
)

def scan_earnings_candidates(today: date) -> list[str]:
  """
  Henter earnings-data og returnerer tradebare earnings-kandidater.
  """
  raw_events = get_earnings_calendar(
    start_date=today,
    days_ahead=1,
  )

  earnings_events = parse_finnhub_earnings_events(raw_events)

  return find_earnings_candidates(
    earnings=earnings_events,
    today=today,
  )

def scan_earnings_candidate_events(today: date):
  """
  Scanner earnings candidates og beholder earnings event-data.
  """
  raw_events = get_earnings_calendar(today)
  events = parse_finnhub_earnings_events(raw_events)

  return find_earnings_candidate_events(
    earnings=events,
    today=today,
  )