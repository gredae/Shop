from datetime import datetime, timedelta

def eta_second(s):
    now = datetime.now().timestamp()
    utc_now = datetime.utcfromtimestamp(now)
    return utc_now + timedelta(seconds=s)

def eta_minutes(m):
    now = datetime.now().timestamp()
    utc_now = datetime.utcfromtimestamp(now)
    return utc_now + timedelta(minutes=m)

def eta_hours(h):
    now = datetime.now().timestamp()
    utc_now = datetime.utcfromtimestamp(now)
    return utc_now + timedelta(hours=h)
