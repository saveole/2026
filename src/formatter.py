"""Data formatting module for sleep/wake entries."""

import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)


def format_sleep_entry(
    entry_date: date,
    sleep_time: Optional[datetime],
    wake_time: Optional[datetime]
) -> str:
    """
    Format sleep data as Chinese text: YYYY-MM-DD: 昨日睡觉 HH:MM 今天起床 HH:MM

    Args:
        entry_date: The date for the entry (typically the wake date)
        sleep_time: Sleep start time (naive datetime in local timezone), or None if missing
        wake_time: Wake time (naive datetime in local timezone), or None if missing

    Returns:
        Formatted string in Chinese format

    Examples:
        >>> format_sleep_entry(
        ...     date(2026, 1, 6),
        ...     datetime(2026, 1, 5, 23, 30),
        ...     datetime(2026, 1, 6, 7, 0)
        ... )
        '2026-01-06: 昨日睡觉 23:30 今天起床 07:00'
    """
    # Format times as HH:MM
    sleep_str = _format_time(sleep_time) if sleep_time else "数据缺失"
    wake_str = _format_time(wake_time) if wake_time else "数据缺失"

    # Format as: YYYY-MM-DD: 昨日睡觉 HH:MM 今天起床 HH:MM
    result = f"{entry_date.isoformat()}: 昨日睡觉 {sleep_str} 今天起床 {wake_str}"

    logger.debug(f"Formatted sleep entry: {result}")
    return result


def _format_time(dt: datetime) -> str:
    """
    Format datetime as HH:MM with leading zeros.

    Args:
        dt: Datetime object (assumed to be in local timezone)

    Returns:
        Time string in 24-hour format with leading zeros

    Examples:
        >>> _format_time(datetime(2026, 1, 6, 7, 5))
        '07:05'
        >>> _format_time(datetime(2026, 1, 6, 23, 30))
        '23:30'
    """
    return dt.strftime("%H:%M")


def determine_entry_date(sleep_time: datetime, wake_time: datetime) -> date:
    """
    Determine the entry date based on wake time (handles midnight crossover).

    The entry date should be the wake date, not the sleep date.
    For example, sleeping at 23:30 and waking at 07:00 next day
    should attribute to the wake date.

    Args:
        sleep_time: Sleep start time (local datetime)
        wake_time: Wake time (local datetime)

    Returns:
        The date for the entry (typically wake date)

    Examples:
        >>> sleep = datetime(2026, 1, 5, 23, 30)
        >>> wake = datetime(2026, 1, 6, 7, 0)
        >>> determine_entry_date(sleep, wake)
        datetime.date(2026, 1, 6)
    """
    # Use wake time's date
    return wake_time.date()
