import functools
import hashlib
import random
import string
from typing import Union, Optional


def md5(_str: Union[str, bytes]) -> Optional[str]:
    """ md5 string """
    if isinstance(_str, bytes):
        return hashlib.md5(_str).hexdigest()
    elif isinstance(_str, str):
        return hashlib.md5(_str.encode()).hexdigest()


def rstr(n: int = 32) -> str:  # noqa
    """ random string """
    return ''.join(random.choices(
        string.digits + string.ascii_lowercase + string.ascii_uppercase,
        k=n
    ))


def ip_to_int(ip: str):
    """ IP convert to int """
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
