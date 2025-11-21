"""
Utility functions for handling datetime operations with timezone support.
The unified timezone used is UTC but for any display purposes, Asia/Taipei (UTC+8) is used.
"""
from datetime import datetime, timezone

import pytz

default_timezone = pytz.timezone('Asia/Taipei')

def get_line_datetime_string_format(timestamp, tz = default_timezone):
    """Convert LINE timestamp (milliseconds since epoch) to formatted datetime string."""
    return datetime.fromtimestamp(timestamp / 1000, tz).strftime('%Y-%m-%dT%H:%M')

def to_utc_datetime(datetime_str):
    """Convert a datetime string in local timezone to UTC datetime object."""
    return datetime.fromisoformat(datetime_str).astimezone(timezone.utc)

def to_local_datetime(utc_datetime, tz = default_timezone):
    """Convert a UTC datetime object to local timezone datetime object."""
    return utc_datetime.astimezone(tz)

def get_local_datetime(tz = default_timezone):
    """Get the current local datetime in the specified timezone."""
    return datetime.now(tz)

def is_earlier_than_now(utc_datetime):
    """Check if the given UTC datetime is earlier than the current UTC time."""
    now_utc = datetime.now(timezone.utc)
    return utc_datetime < now_utc
