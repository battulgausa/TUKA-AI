from datetime import datetime
from zoneinfo import ZoneInfo

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def worker_allowed_now(tz_name: str = "America/Chicago",
                       start_hm: str = "08:00",
                       end_hm: str = "17:00") -> bool:
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)

    day = now.strftime("%a")  # Mon, Tue, ...
    if day not in DAYS:
        return False

    sh, sm = [int(x) for x in start_hm.split(":")]
    eh, em = [int(x) for x in end_hm.split(":")]

    start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end = now.replace(hour=eh, minute=em, second=0, microsecond=0)

    return start <= now <= end
