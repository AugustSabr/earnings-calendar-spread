import pytest

from earnings_calendar_spreads.core.term_structure import build_term_structure


def test_estimates_iv_between_known_expirations():
  term_structure = build_term_structure(
    days=[10, 20],
    ivs=[0.60, 0.40],
  )

  result = term_structure(15)

  assert result == 0.50


def test_uses_first_iv_before_known_range():
  term_structure = build_term_structure(
    days=[10, 20],
    ivs=[0.60, 0.40],
  )

  result = term_structure(5)

  assert result == 0.60


def test_uses_last_iv_after_known_range():
  term_structure = build_term_structure(
    days=[10, 20],
    ivs=[0.60, 0.40],
  )

  result = term_structure(30)

  assert result == 0.40


def test_sorts_points_before_estimating():
  term_structure = build_term_structure(
    days=[20, 10],
    ivs=[0.40, 0.60],
  )

  result = term_structure(15)

  assert result == 0.50


def test_raises_error_when_lengths_do_not_match():
  with pytest.raises(ValueError):
    build_term_structure(
      days=[10, 20],
      ivs=[0.60],
    )


def test_raises_error_without_points():
  with pytest.raises(ValueError):
    build_term_structure(
      days=[],
      ivs=[],
    )