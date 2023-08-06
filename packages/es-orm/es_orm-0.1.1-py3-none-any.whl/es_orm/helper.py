import datetime
import decimal
import hashlib
import json
import uuid

from typing import Union


def md5(data: Union[str, bytes]):
    if data and isinstance(data, str):
        return hashlib.md5(data.encode()).hexdigest()
    elif data and isinstance(data, bytes):
        return hashlib.md5(data).hexdigest()


class JsonDecoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        self.date_f = '%Y-%m-%d'
        self.date_time_f = self.date_f + ' %H:%M:%S'
        super().__init__(*args, **kwargs)

    @staticmethod
    def _get_duration_components(duration):
        days = duration.days
        seconds = duration.seconds
        microseconds = duration.microseconds

        minutes = seconds // 60
        seconds = seconds % 60

        hours = minutes // 60
        minutes = minutes % 60
        return days, hours, minutes, seconds, microseconds

    def duration_iso_string(self, duration):
        if duration < datetime.timedelta(0):
            sign = '-'
            duration *= -1
        else:
            sign = ''

        days, hours, minutes, seconds, microseconds = self._get_duration_components(duration)
        ms = '.{:06d}'.format(microseconds) if microseconds else ""
        return '{}P{}DT{:02d}H{:02d}M{:02d}{}S'.format(sign, days, hours, minutes, seconds, ms)

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime(self.date_time_f)
        elif isinstance(o, datetime.date):
            return o.strftime(self.date_f)
        elif isinstance(o, datetime.time):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return self.duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        else:
            return super().default(o)


def json_dump(data):
    return json.dumps(data, cls=JsonDecoder)


class Result(object):
    """ es result obj """

    class Data(dict):
        """ result obj """

        def __init__(self, *args, **kwargs):
            super(self.__class__, self).__init__(*args, **kwargs)

        def __add__(self, other: dict):
            for k, v in other.items():
                self.__setitem__(k, v)

        def __setitem__(self, key, value):
            if isinstance(value, dict):
                super().__setitem__(key, self.__class__(**value))
            else:
                super().__setitem__(key, value)

        def __getattribute__(self, item):
            try:
                return super().__getattribute__(item)
            except:
                return self.get(item)

    def __init__(self, result: dict):
        self.result: dict = result

    def total(self):
        return int(self.result.get('hits', {}).get('total', {}).get('value', 0))

    def hits(self):
        """ 获取查询数据列表 """
        return self.result.get('hits', {}).get('hits', [])

    def scroll_id(self):
        return self.result.get('_scroll_id', '')

    def __iter__(self):
        """ 遍历结果 """
        for item in self.hits():
            yield self.Data(source_id=item["_id"], **item['_source'])
