from typing import Dict, List, Any, Protocol
import fcntl
from hashlib import sha256
import random
from datetime import datetime, timedelta
from functools import wraps

import jwt

from boot.config import Config


def get_uuid(ref: str = '') -> str:
    """Naive way to get uuid
    """
    return sha256(random.randbytes(32) + ref.encode() + random.randbytes(32)).hexdigest()


def hash_passwd(passwd: str) -> str:
    hasded = passwd.encode()
    for _ in range(Config.hash_rounds):
        hasded = sha256(hasded + Config.salt.encode()).digest()
    return hasded.hex()


def auth_sign(data: Dict[str, Any]) -> str:
    expire = now_time() + timedelta(days=7)
    data.update(expire=expire.strftime('%Y-%m-%d %H:%M'))
    return jwt.encode(data, Config.jwt_secret, algorithm='HS256')


def auth_verify(token: str) -> str:
    try:
        return jwt.decode(token, key=Config.jwt_secret, algorithms=['HS256'])['user']
    except jwt.exceptions.DecodeError:
        return ''

def now_time() -> datetime:
    return datetime.utcnow() + timedelta(hours=8)


class ArbitraryCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

class SupportsStr(Protocol):

    def __str__(self) -> str:
        ...


class FLock:
    """As gstore does not support concurrency
    Add our lock explicitly
    """

    def __init__(self, file_path: str) -> None:
        self.fd = open(file_path + '.lock', 'a')

    def __enter__(self):
        fcntl.flock(self.fd, fcntl.LOCK_EX)

    def __exit__(self, exc_type, exc_value, exc_tb):
        fcntl.flock(self.fd, fcntl.LOCK_UN)

    def __call__(self, f: ArbitraryCallable) -> ArbitraryCallable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any):
            with self:
                f(*args, **kwargs)
        return wrapper


glock = FLock('global')


def test_flock():
    print('Testing flock...')
    with FLock('test.lock'):
        print('Seems all right.')

    def subtest():
        with FLock('test.lock'):
            with FLock('test.lock'):
                print('RLock')
    from func_timeout import func_timeout
    try:
        func_timeout(0.5, subtest)
    except:
        print('Not RLock')


def pagination(size: int, page: int, li: List[Any]) -> List[Any]:
    return li[(page - 1) * size: page * size]
