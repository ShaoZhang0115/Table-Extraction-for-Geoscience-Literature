import json
import os
from typing import Union


class BaseConfigManager(object):
    @classmethod
    def get_int(cls, key: str, default=None) -> Union[int, None]:
        raise NotImplementedError

    @classmethod
    def get_str(cls, key: str, default=None) -> Union[str, None]:
        raise NotImplementedError

    @classmethod
    def get_dict(cls, key: str, default=None) -> Union[dict, None]:
        raise NotImplementedError


class EnvironConfig(BaseConfigManager):
    @classmethod
    def _get(cls, key: str, default=None):
        if not isinstance(key, str):
            raise TypeError

        value = os.environ.get(key, default=default)
        if value is None:
            return None
        if value == "null":
            return None
        return value

    @classmethod
    def get_int(cls, key: str, default: int = None) -> Union[int, None]:
        value = cls._get(key, default=default)
        return int(value)

    @classmethod
    def get_str(cls, key: str, default: str = None) -> Union[str, None]:
        value = cls._get(key, default=default)
        return str(value)

    @classmethod
    def get_dict(cls, key: str, default: dict = None) -> Union[dict, None]:
        value = cls._get(key, default=default)
        if isinstance(value, str):
            return json.loads(value)
        elif isinstance(value, dict):
            return value
        else:
            raise ValueError
