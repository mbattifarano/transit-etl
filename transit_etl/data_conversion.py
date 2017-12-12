"""Raw data conversion tools"""
import datetime as dt


def to_fullyear(two_digit_year):
    return int("20"+two_digit_year)


def trim(s):
    return s.strip()


def to_datetime(year, month, day, hour, minute, second=0):
    offset = dt.timedelta(days=1) if hour == 25 else dt.timedelta(0)
    hr = hour if hour < 25 else 1
    try:
        day = dt.date(year, month, day) + offset
        time = dt.time(hr, minute, second)
    except ValueError:
        return None
    else:
        return dt.datetime.combine(day, time)


def split_concatenated_time(t):
    hour = t[0:2]
    minute = t[1:3]
    return hour, minute


def format_block_id(block):
    return '-'.join([block[0:3], block[2:5]])