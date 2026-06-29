from datetime import date

from earnings_calendar_spreads.workflow.screen_candidates import (
  screen_earnings_candidates,
)


def format_pass(value: bool) -> str:
  """
  Formaterer en boolsk pass/fail-verdi for terminal-output.
  """
  return "PASS" if value else "FAIL"


def main():
  today = date.today()

  results = screen_earnings_candidates(today=today)

  qualified = [
    result
    for result in results
    if result.qualifies
  ]

  print(f"Screening results for {today}")
  print(f"Screened: {len(results)}")
  print(f"Qualified: {len(qualified)}")

  print()
  print(
    f"{'Symbol':<8}"
    f"{'Qualifies':<12}"
    f"{'Volume':<10}"
    f"{'IV/RV':<10}"
    f"{'TS Slope':<10}"
    f"{'Exp Move':<10}"
  )

  for result in results:
    qualifies = "YES" if result.qualifies else "NO"

    print(
      f"{result.symbol:<8}"
      f"{qualifies:<12}"
      f"{format_pass(result.passes_average_volume):<10}"
      f"{format_pass(result.passes_iv30_rv30):<10}"
      f"{format_pass(result.passes_term_structure_slope):<10}"
      f"{str(result.expected_move):<10}"
    )

  print("\nQualified symbols:")
  if not qualified:
    print("No qualified symbols found.")
    return

  for result in qualified:
    print(f"- {result.symbol}")


if __name__ == "__main__":
  main()