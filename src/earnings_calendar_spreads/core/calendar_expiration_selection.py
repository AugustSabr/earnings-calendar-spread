from datetime import date, timedelta


def select_calendar_expirations(
  expiration_dates: list[str],
  entry_date: date,
  earnings_date: date,
  target_long_dte: int = 45,
) -> tuple[str, str]:
  """
  Velger short og long expiration for calendar spread.

  Short leg:
  - første expiration på eller etter earnings_date

  Long leg:
  - første expiration på eller etter entry_date + target_long_dte
  """
  if not expiration_dates:
    raise ValueError("expiration_dates cannot be empty.")

  sorted_expirations = sorted(
    date.fromisoformat(expiration_date)
    for expiration_date in expiration_dates
  )

  short_expiration = next(
    (
      expiration
      for expiration in sorted_expirations
      if expiration >= earnings_date
    ),
    None,
  )

  if short_expiration is None:
    raise ValueError("No short expiration found after earnings_date.")

  target_long_date = entry_date + timedelta(days=target_long_dte)

  long_expiration = next(
    (
      expiration
      for expiration in sorted_expirations
      if expiration >= target_long_date and expiration > short_expiration
    ),
    None,
  )

  if long_expiration is None:
    raise ValueError("No long expiration found near target_long_dte.")

  return (
    short_expiration.isoformat(),
    long_expiration.isoformat(),
  )