from datetime import datetime, timedelta
import pytz

from backend.src.utils.constants import TIMEZONE
from backend.src.utils.exceptions import UserError


def convert_to_utc(local_date_str, is_start=True):
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

        return utc_date
    except ValueError:
        raise UserError('Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM')


def convert_to_local(utc_date, tz_name='Asia/Jerusalem'):
    """

    """
    local_tz = pytz.timezone(tz_name)
    return utc_date.astimezone(local_tz)

