# tests/test_date_services.py
from datetime import UTC, datetime

import pytest

from services.date_services import (
    format_french_datetime,
    format_utc_datetime,
)


# --- Tests for format_french_datetime ---
def test_format_french_datetime_utc_aware_winter():
    dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
    assert format_french_datetime(dt) == "15/01/2024 (13:00:00)"


def test_format_french_datetime_naive():
    dt = datetime(2024, 1, 15, 12, 0, 0)  # noqa: DTZ001
    assert format_french_datetime(dt) == "15/01/2024 (13:00:00)"


def test_format_french_datetime_none():
    assert format_french_datetime(None) == "N/A"


def test_format_french_datetime_dst_summer():
    dt = datetime(2024, 7, 15, 12, 0, 0, tzinfo=UTC)
    assert format_french_datetime(dt) == "15/07/2024 (14:00:00)"


# --- Tests for format_utc_datetime ---
def test_format_utc_datetime_valid_winter():
    assert format_utc_datetime("15/01/2024 (13:00:00)") == datetime(
        2024, 1, 15, 12, 0, 0, tzinfo=UTC
    )


def test_format_utc_datetime_na():
    assert format_utc_datetime("N/A") is None
    assert format_utc_datetime(None) is None


def test_format_utc_datetime_invalid_format():
    with pytest.raises(ValueError):
        format_utc_datetime("15/01/2024")
