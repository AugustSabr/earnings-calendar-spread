import os

from dotenv import load_dotenv

def get_finnhub_api_key(load_env_file: bool = True) -> str:
  """
  Henter Finnhub API-nøkkelen fra miljøvariabler eller .env-filen.
  """
  if load_env_file:
    load_dotenv()

  api_key = os.getenv("FINNHUB_API_KEY")

  if not api_key:
    raise ValueError("FINNHUB_API_KEY mangler. Legg den i .env-filen.")

  return api_key