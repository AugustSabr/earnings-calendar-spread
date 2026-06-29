from datetime import date, datetime, timedelta

def filter_expiration_dates(
  expiration_dates: list[str],
  today: date,
  min_days_out: int = 45,
) -> list[str]:
  """
  Returnerer option-expirations frem til første dato som er minst min_days_out dager frem.
  - sorter datoene
  - inkluder expiries opp til og med første expiry minst 45 dager frem
  - fjern dagens expiry hvis den ligger først
  """
  cutoff_date = today + timedelta(days=min_days_out)

  sorted_dates = sorted(
    datetime.strptime(expiration_date, "%Y-%m-%d").date()
    for expiration_date in expiration_dates
  )

  selected_dates = []

  for index, expiration_date in enumerate(sorted_dates):
    if expiration_date >= cutoff_date:
      selected_dates = [
        selected_date.strftime("%Y-%m-%d")
        for selected_date in sorted_dates[:index + 1]
      ]
      break

  if not selected_dates:
    raise ValueError("No expiration date far enough in the future found.")

  if selected_dates[0] == today.strftime("%Y-%m-%d"):
    return selected_dates[1:]

  return selected_dates