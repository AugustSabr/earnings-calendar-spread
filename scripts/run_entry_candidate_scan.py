from datetime import date

from earnings_calendar_spreads.workflow.screen_candidates import (
  screen_earnings_candidate_events,
)

def format_pass(value: bool) -> str:
  return "PASS" if value else "FAIL"

def main():
  today = date.today()

  candidates = screen_earnings_candidate_events(
    today=today,
  )

  qualified = [
    candidate
    for candidate in candidates
    if candidate.screening_result.qualifies
  ]

  print(f"Entry candidate scan for {today}")
  print(f"Screened: {len(candidates)}")
  print(f"Qualified: {len(qualified)}")
  print()

  print(
    f"{'Symbol':<8}"
    f"{'Earnings':<12}"
    f"{'Time':<8}"
    f"{'Qualifies':<10}"
    f"{'Volume':<10}"
    f"{'IV/RV':<10}"
    f"{'Slope':<10}"
    f"{'Exp Move':<10}"
  )

  for candidate in candidates:
    event = candidate.earnings_event
    result = candidate.screening_result

    print(
      f"{result.symbol:<8}"
      f"{event.report_date.isoformat():<12}"
      f"{str(event.report_time):<8}"
      f"{'YES' if result.qualifies else 'NO':<10}"
      f"{format_pass(result.passes_average_volume):<10}"
      f"{format_pass(result.passes_iv30_rv30):<10}"
      f"{format_pass(result.passes_term_structure_slope):<10}"
      f"{str(result.expected_move):<10}"
    )

  print()
  print("Qualified candidates:")

  if not qualified:
    print("No qualified candidates found.")
    return

  for candidate in qualified:
    event = candidate.earnings_event
    result = candidate.screening_result

    print(
      f"- {result.symbol} "
      f"earnings={event.report_date.isoformat()} "
      f"time={event.report_time} "
      f"expected_move={result.expected_move}"
    )

if __name__ == "__main__":
  main()