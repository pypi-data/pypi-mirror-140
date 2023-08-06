import json
import datetime


def md5(_str):
    """ md5 string """
    import hashlib
    if isinstance(_str, bytes):
        return hashlib.md5(_str).hexdigest()
    elif isinstance(_str, str):
        return hashlib.md5(_str.encode()).hexdigest()


def rstr(n: int = 32) -> str:  # noqa
    """ random string """
    import random, string
    return ''.join(random.choices(
        string.digits + string.ascii_lowercase + string.ascii_uppercase,
        k=n
    ))


def ip_to_int(ip: str):
    """ IP convert to int """
    import functools
    # 192.168.1.13
    # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
    return functools.reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


def int_to_ip(ip: int) -> str:
    """ int ip num to ip str
        tmp1 = ip >> 24
        tmp2 = (ip >> 16) - (tmp1 << 8)
        tmp3 = (ip >> 8) - (tmp1 << 16) - (tmp2 << 8)
        tmp4 = ip - (tmp1 << 24) - (tmp2 << 16) - (tmp3 << 8)
    """

    def inner(lst=[], times=3):
        tmp = ip >> times * 8
        for idx, item in enumerate(reversed(lst)):
            tmp -= item << (idx + 1) * 8
        lst.append(tmp)
        if times > 0:
            return inner(times=times - 1)
        return lst

    return '{}.{}.{}.{}'.format(*inner())


class JSONEncoder(json.JSONEncoder):
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
        import uuid, decimal
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


def obj_hook(obj, fmt=None):
    from copy import deepcopy

    time_fmt = [
        '%d/%m/%Y %H:%M%S', '%d/%m/%Y %H:%M%S.%f', '%d/%m/%YT%H:%M%S.%f'
                                                   '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'
    ]

    if fmt and isinstance(fmt, list):
        time_fmt.extend(fmt)
    elif fmt and isinstance(fmt, str):
        time_fmt.append(fmt)

    if isinstance(obj, list):
        tmp = enumerate(obj)
    elif isinstance(obj, dict):
        tmp = obj.items()
    else:
        return obj

    ret = deepcopy(obj)
    for k, v in tmp:
        if isinstance(v, str):
            for f in time_fmt:
                try:
                    ret[k] = datetime.datetime.strptime(v, f)
                except:
                    ...
        elif isinstance(v, (list, dict)):
            ret[k] = obj_hook(v)
    return ret


def json_dump(data):
    return json.dumps(data, cls=JSONEncoder)


def json_load(data: str):
    return json.loads(data, object_hook=obj_hook)
