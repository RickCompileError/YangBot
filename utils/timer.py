"""
Utility functions for handling datetime operations with timezone support.
The unified timezone used is UTC but for any display purposes, Asia/Taipei (UTC+8) is used.
"""
import logging
import time
from datetime import datetime, timezone

import pytz

default_timezone = pytz.timezone('Asia/Taipei')


def get_line_datetime_string_format(timestamp, tz = default_timezone):
    """Convert LINE timestamp (milliseconds since epoch) to formatted datetime string."""
    return datetime.fromtimestamp(timestamp / 1000, tz).strftime('%Y-%m-%dT%H:%M')

def to_utc_datetime(datetime_str):
    """Convert a datetime string in local timezone to UTC datetime object."""
    naive_dt = datetime.fromisoformat(datetime_str)
    local_dt = default_timezone.localize(naive_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)
    return utc_dt

def to_local_datetime(utc_datetime, tz = default_timezone):
    """Convert a UTC datetime object to local timezone datetime object."""
    return utc_datetime.astimezone(tz)

def is_earlier_than_now(utc_datetime):
    """Check if the given UTC datetime is earlier than the current UTC time."""
    now_utc = datetime.now(timezone.utc)
    return utc_datetime < now_utc

def get_tzname():
    return time.tzname

logging.info("Python timezone: %s", get_tzname())
logging.info("Current datetime: %s", datetime.now())
logging.info("UTC datetime: %s", datetime.now(pytz.UTC))
logging.info("Asia/Taipei datetime: %s", datetime.now(default_timezone))
