from hashlib import sha256
from functools import wraps
import re

def type_check_setter_data(func):
    @wraps(func)
    def wrapper(self, new_data: str):
        if type(new_data) is not str:
            raise TypeError('новые данные должны быть типа str')
        return func(self, new_data)
    return wrapper

def type_check_eq(func):
    @wraps(func)
    def wrapper(self: Sha256Hash, other: Sha256Hash):
        if not isinstance(other, Sha256Hash):
            return False
        if not self.hashed_data:
            self.generate_hash()
        if not other.hashed_data:
            other.generate_hash()
        return func(self, other)
    return wrapper

class Sha256Hash:

    def __init__(self, data: str | None = None):
        if data:
            self.data = data
        self._hashed_data: str = ''
        self.hasher = sha256()

    @property
    def data(self) -> str:
        return self._data

    @data.setter
    @type_check_setter_data
    def data(self, new_data: str):
        self._data = new_data
        self.generate_hash()

    @property
    def hashed_data(self) -> str:
        self._hashed_data = self.hasher.hexdigest()
        return self._hashed_data

    def generate_hash(self):
        self._hashed_data = self.hasher.hexdigest()
        return self._hashed_data

    def append_hash_chunk(self, chunk: bytes):
        self.hasher.update(chunk)

    @staticmethod
    def string_is_hash(data: str) -> bool:
        pattern = r"[0-9A-Fa-f]{64}"
        return bool(re.match(pattern, data))

    @type_check_eq
    def __eq__(self, other: Sha256Hash):
        if all(map(
                self.string_is_hash,
                [self._hashed_data, other._hashed_data]
        )):
            return self._hashed_data == other._hashed_data
        return False