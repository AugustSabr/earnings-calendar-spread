import pytest

from earnings_calendar_spreads.config import get_finnhub_api_key


def test_get_finnhub_api_key(monkeypatch):
  monkeypatch.setenv("FINNHUB_API_KEY", "test-key")

  result = get_finnhub_api_key(load_env_file=False)

  assert result == "test-key"


def test_get_finnhub_api_key_raises_error_when_missing(monkeypatch):
  monkeypatch.delenv("FINNHUB_API_KEY", raising=False)

  with pytest.raises(ValueError):
    get_finnhub_api_key(load_env_file=False)