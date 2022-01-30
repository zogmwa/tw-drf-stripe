import datetime
from datetime import datetime as datetime_datetime


def convert_string_to_datetime(string):
    return datetime_datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")


def convert_string_to_date(string):
    return datetime_datetime.strptime(string[:10], "%Y-%m-%d")


def get_now_converted_google_date():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
