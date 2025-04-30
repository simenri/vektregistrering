from datetime import datetime
from zoneinfo import ZoneInfo

def get_todays_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_timestamp():
    oslo_time = datetime.now(ZoneInfo("Europe/Oslo"))
    return oslo_time.strftime("%Y-%m-%d %H:%M:%S")