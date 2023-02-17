import logging
from typing import Dict, List

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AcemapBaseModel(BaseModel):
    def __getattribute__(self, attr: str):
        if attr in super().__getattribute__("__fields__") and attr not in super().__getattribute__("__fields_set__"):
            raise AttributeError(
                f"Attribute '{attr}' of {self.__class__.__name__} is not allowed to access, "
                f"Please Check your 'includes' limitation."
            )
        return super().__getattribute__(attr)

    @staticmethod
    def _flatten(items):
        for x in items:
            if isinstance(x, (list, set, tuple)):
                yield from AcemapBaseModel._flatten(x)
            elif isinstance(x, dict):
                yield from AcemapBaseModel._flatten(x.values())
            else:
                yield x

    def _enable_access(self, access_tree: Dict, reset: bool = False):
        if reset:
            self.__fields_set__.clear()
        for attr in self.__fields__:
            if not access_tree or attr in access_tree:
                self.__fields_set__.add(attr)
                value = self.__getattribute__(attr)
                if isinstance(value, (list, set, tuple)):
                    values = value
                elif isinstance(value, dict):
                    values = value.values()
                else:
                    values = [value]
                next_access_tree = access_tree.get(attr, {})
                for item in self._flatten(values):
                    if isinstance(item, AcemapBaseModel):
                        item._enable_access(next_access_tree, reset)

    def enable_access(self, allow_access: List[str] = None, reset: bool = False):
        """设置只能访问特定的字段

        Parameters
        ----------
        allow_access
            允许访问哪些字段，可传入list或None。
            若设置为None，则允许访问所有字段。
            若设置为[]，且reset为True，则禁止访问所有字段
        reset
            是否重置已有的可以访问的字段。
            若为False，则原本已经可访问的字段后续可继续访问，即增加allow_access内传入的字段。
            若为True，则原本可访问的字段后续无法继续访问，除非在allow_access也进行了声明，即重置为allow_access内传入的字段
        Returns
        -------
        None
        """
        if reset:
            self.__fields_set__.clear()
        if allow_access == []:
            return
        access_tree = {}
        for path in allow_access or []:
            path = path.strip().split(".")
            current_node = access_tree
            for item in path:
                if item not in current_node:
                    current_node[item] = {}
                current_node = current_node[item]
        # logger.info(f'{access_tree}, {reset}')
        self._enable_access(access_tree, reset)
        self.__fields_set__.add("id")


class CountPerYear(AcemapBaseModel):
    year: int = 0
    value: int = 0


class MapInfo(AcemapBaseModel):
    field_id: int = 0
    type: str = ""
    title: str = ""
    image: str = ""
    node_type: str = ""  # Now only support 'paper' or 'author'
