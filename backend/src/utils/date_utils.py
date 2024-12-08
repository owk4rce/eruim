from datetime import datetime, timedelta
import pytz

from backend.src.utils.constants import TIMEZONE
from backend.src.utils.exceptions import UserError

import logging

logger = logging.getLogger('backend')


def convert_to_utc(local_date_str, is_start=True):
    """
    Convert local datetime string to UTC datetime object.

    Handles two date string formats:
    - "YYYY-MM-DD HH:MM" - specific time
    - "YYYY-MM-DD" - date only (converts to start or end of day)

    Args:
        local_date_str (str): Date(time) string in local timezone
        is_start (bool): For date-only strings, if True converts to 00:00,
                        if False converts to 23:59 (default: True)

    Returns:
        datetime: UTC datetime object

    Raises:
        UserError: If date string format is invalid
    """
    try:
        # looking for time
        if " " in local_date_str:
            # if time exists, parse date + time
            local_date = datetime.strptime(local_date_str, "%Y-%m-%d %H:%M")
        else:
            # just date
            local_date = datetime.strptime(local_date_str, "%Y-%m-%d")

            if not is_start:
                # end_date = 23:59
                local_date += timedelta(hours=23, minutes=59)

        # setting local tz
        local_date = TIMEZONE.localize(local_date)

        # convert to UTC
        utc_date = local_date.astimezone(pytz.UTC)

        logger.debug(f"Converted {local_date_str} to UTC: {utc_date}")

        return utc_date
    except ValueError:
        raise UserError('Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM')


def convert_to_local(utc_date, tz_name='Asia/Jerusalem'):
    """
    Convert UTC datetime to local timezone.
    If input date has no timezone info, assumes it's UTC.
    """
    # Explicitly treat naive datetime as UTC
    if not utc_date.tzinfo:
        utc_date = pytz.UTC.localize(utc_date)

    # Convert to target timezone
    target_tz = pytz.timezone(tz_name)

    return utc_date.astimezone(target_tz)


def remove_timezone(dt):
    # check if we have tz
    if dt.tzinfo:
        # replace tz to None
        dt_without_timezone = dt.replace(tzinfo=None)
    else:
        dt_without_timezone = dt

    logger.debug(f"Removed timezone: {dt_without_timezone}")

    return dt_without_timezone
