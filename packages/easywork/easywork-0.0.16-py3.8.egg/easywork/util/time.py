import datetime
import time as _time

from dateutil.relativedelta import relativedelta

FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
FORMAT_DATE = '%Y-%m-%d'


def sleep(seconds):
    _time.sleep(seconds)


def now():
    return datetime.datetime.now()


def today():
    return format(now(), FORMAT_DATE)


def current():
    return format(now(), FORMAT_DATETIME)


def strftime(date: datetime.datetime, fmt: str = FORMAT_DATETIME):
    return date.strftime(fmt)


def strptime(value: str, fmt: str = FORMAT_DATETIME):
    return datetime.datetime.strptime(value, fmt)


def fromdate(date: datetime.date):
    return datetime.datetime(date.year, date.month, date.day)


def todate(date: datetime.datetime):
    return datetime.datetime.date(date)


def fromtimestamp(value: int):
    return datetime.datetime.fromtimestamp(value / 1000)


def totimestamp(date: datetime.datetime):
    return int(f'{int(_time.mktime(date.timetuple()))}{str(date.microsecond)[:3]}')


def offset_years(date: datetime.datetime, unit: int):
    return date + relativedelta(years=unit)


def offset_months(date: datetime.datetime, unit: int):
    return date + relativedelta(months=unit)


def offset_days(date: datetime.datetime, unit: int):
    return date + relativedelta(days=unit)


def offset_weeks(date: datetime.datetime, unit: int):
    return date + relativedelta(weeks=unit)


def offset_hours(date: datetime.datetime, unit: int):
    return date + relativedelta(hours=unit)


def offset_minutes(date: datetime.datetime, unit: int):
    return date + relativedelta(minutes=unit)


def offset_seconds(date: datetime.datetime, unit: int):
    return date + relativedelta(seconds=unit)


def differ_years(date1: datetime.datetime, date2: datetime.datetime):
    return date1.year - date2.year


def differ_months(date1: datetime.datetime, date2: datetime.datetime):
    return differ_years(date1, date2) * 12 + date1.month - date2.month


def differ_weeks(date1: datetime.datetime, date2: datetime.datetime):
    return differ_days(date1, date2) // 7


def differ_days(date1: datetime.datetime, date2: datetime.datetime):
    return (todate(date1) - todate(date2)).days


def differ_hours(date1: datetime.datetime, date2: datetime.datetime):
    return differ_seconds(date1, date2) // 3600


def differ_minutes(date1: datetime.datetime, date2: datetime.datetime):
    return differ_seconds(date1, date2) // 60


def differ_seconds(date1: datetime.datetime, date2: datetime.datetime):
    return int((date1 - date2).total_seconds())
