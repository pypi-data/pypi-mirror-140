import random
import time
from datetime import datetime

STANDARD_FORMAT = {
    'isoDateTime': '%Y-%m-%dT%H:%M:%SZ',
    'datetime': '%Y-%m-%d %H:%M:%S',
    'date': '%Y-%m-%d',
    'time': '%H:%M:%S',
    'month': '%Y-%m',
    'dbdt': '%Y%m%d_%H%M%S'
}


class Date:
    @classmethod
    def format(cls, in_date=None, in_fmt='datetime'):
        date = in_date or datetime.now()
        fmt = STANDARD_FORMAT[in_fmt] or in_fmt
        return date.strftime(fmt)

    @classmethod
    def now(cls):
        return int(datetime.now().timestamp())

    @classmethod
    def create(cls, target):
        if type(target) is str:
            return datetime.fromisoformat(target)
        if type(target) is int:
            return datetime.fromtimestamp(target)
        if type(target) is datetime:
            return target
        return None

    @classmethod
    def random_date(cls, start, end, in_fmt='datetime', in_min_gap=75):
        prop = random.random()
        fmt = STANDARD_FORMAT[in_fmt] or in_fmt
        stime = time.mktime(time.strptime(start, fmt))
        etime = time.mktime(time.strptime(end, fmt))
        gap = prop * (etime - stime)
        if gap < in_min_gap:
            gap = in_min_gap
        ptime = stime + gap
        return time.strftime(fmt, time.localtime(ptime))

    @classmethod
    def random_date_list(cls, start, end, in_fmt='datetime', in_min_gap=75, in_count=10):
        no_unique_list = []
        fmt = STANDARD_FORMAT[in_fmt] or in_fmt
        for i in range(in_count * 2):
            last_el = no_unique_list[-1] if len(no_unique_list) > 0 else start
            no_unique_list.append(cls.random_date(last_el, end, in_fmt, in_min_gap))
        res = list(set(no_unique_list))[:in_count]
        res.sort(key=lambda date: time.strptime(date, '%Y-%m-%d %H:%M:%S'))
        return res
