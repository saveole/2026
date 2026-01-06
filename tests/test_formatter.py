"""Unit tests for data formatter module."""

import pytest
from datetime import datetime, date

from src.formatter import (
    format_sleep_entry,
    determine_entry_date,
    _format_time,
)


class TestFormatSleepEntry:
    """Tests for format_sleep_entry function."""

    def test_format_standard_sleep_data(self):
        """Test formatting standard sleep/wake times."""
        entry_date = date(2026, 1, 6)
        sleep_time = datetime(2026, 1, 5, 23, 30)
        wake_time = datetime(2026, 1, 6, 7, 0)

        result = format_sleep_entry(entry_date, sleep_time, wake_time)

        assert result == "2026-01-06: 昨日睡觉 23:30 今天起床 07:00"

    def test_format_midnight_crossover(self):
        """Test formatting when sleep crosses midnight."""
        entry_date = date(2026, 1, 6)
        sleep_time = datetime(2026, 1, 6, 1, 0)
        wake_time = datetime(2026, 1, 6, 7, 0)

        result = format_sleep_entry(entry_date, sleep_time, wake_time)

        assert result == "2026-01-06: 昨日睡觉 01:00 今天起床 07:00"

    def test_format_missing_sleep_time(self):
        """Test formatting when sleep time is None."""
        entry_date = date(2026, 1, 6)
        wake_time = datetime(2026, 1, 6, 7, 0)

        result = format_sleep_entry(entry_date, None, wake_time)

        assert result == "2026-01-06: 昨日睡觉 数据缺失 今天起床 07:00"

    def test_format_missing_wake_time(self):
        """Test formatting when wake time is None."""
        entry_date = date(2026, 1, 6)
        sleep_time = datetime(2026, 1, 5, 23, 30)

        result = format_sleep_entry(entry_date, sleep_time, None)

        assert result == "2026-01-06: 昨日睡觉 23:30 今天起床 数据缺失"

    def test_format_both_missing(self):
        """Test formatting when both times are None."""
        entry_date = date(2026, 1, 6)

        result = format_sleep_entry(entry_date, None, None)

        assert result == "2026-01-06: 昨日睡觉 数据缺失 今天起床 数据缺失"

    def test_24_hour_format_with_leading_zeros(self):
        """Test that times are in 24-hour format with leading zeros."""
        entry_date = date(2026, 1, 6)
        sleep_time = datetime(2026, 1, 5, 9, 5)
        wake_time = datetime(2026, 1, 6, 7, 15)

        result = format_sleep_entry(entry_date, sleep_time, wake_time)

        assert result == "2026-01-06: 昨日睡觉 09:05 今天起床 07:15"


class TestDetermineEntryDate:
    """Tests for determine_entry_date function."""

    def test_date_based_on_wake_time(self):
        """Test that entry date is based on wake time, not sleep time."""
        sleep_time = datetime(2026, 1, 5, 23, 30)
        wake_time = datetime(2026, 1, 6, 7, 0)

        result = determine_entry_date(sleep_time, wake_time)

        assert result == date(2026, 1, 6)

    def test_same_day_sleep_and_wake(self):
        """Test when sleep and wake are on same day."""
        sleep_time = datetime(2026, 1, 6, 1, 0)
        wake_time = datetime(2026, 1, 6, 7, 0)

        result = determine_entry_date(sleep_time, wake_time)

        assert result == date(2026, 1, 6)


class TestFormatTime:
    """Tests for _format_time function."""

    def test_format_with_minutes(self):
        """Test formatting with specific minutes."""
        dt = datetime(2026, 1, 6, 23, 45)

        result = _format_time(dt)

        assert result == "23:45"

    def test_leading_zeros(self):
        """Test that single-digit hours have leading zeros."""
        dt = datetime(2026, 1, 6, 5, 5)

        result = _format_time(dt)

        assert result == "05:05"
