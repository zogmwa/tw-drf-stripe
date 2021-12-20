import datetime


def convert_str_to_google_valid_date(str):
    return str.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_now_converted_google_date():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
