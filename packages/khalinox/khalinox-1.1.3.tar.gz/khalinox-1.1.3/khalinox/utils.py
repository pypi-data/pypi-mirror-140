"""helpers
"""

from cryptography.fernet import Fernet
from toolz import pipe


def _tostr(data: bytes) -> str:
    return data.decode("utf8")


def _tobytes(data: str) -> bytes:
    return bytes(data, "utf8")


def encrypt(key: str, password: str) -> str:
    f = Fernet(_tobytes(key))
    return pipe(password, _tobytes, f.encrypt, _tostr)


def decrypt(key: str, encrypted: str) -> str:
    f = Fernet(_tobytes(key))
    return pipe(encrypted, _tobytes, f.decrypt, _tostr)
