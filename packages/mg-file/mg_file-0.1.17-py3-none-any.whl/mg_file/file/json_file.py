__all__ = ["JsonFile"]

from json import load, dump, JSONDecodeError
from typing import Any, Union, Optional

from .base_file import BaseFile, concat_data


class JsonFile(BaseFile):
    """
    Работа с Json файлами
    """

    def __init__(self, name_file: str, type_file: Optional[str] = ".json"):
        super().__init__(name_file, type_file=type_file)

    def readFile(self, **kwargs) -> Union[list, dict, int, str, float, None, bool]:
        try:
            with open(self.name_file, "r") as _jsonFile:
                return load(_jsonFile)
        except JSONDecodeError:
            return None

    def writeFile(self, data: Union[list, dict, int, str, float, None, bool, tuple],
                  *, indent=4,
                  skipkeys=False,
                  sort_keys=True,
                  ensure_ascii: bool = False):
        """
        :param data: list, dict, int, str, float, None, bool, tuple.
        :param skipkeys: Если False вызовет исключение при неправильном типе данных.
        :param indent: Отступы для записи.
        :param sort_keys: Сортировать ключи.
        :param ensure_ascii: Экранировать символы, если False данные запишутся как есть.
        """
        with open(self.name_file, "w") as _jsonFile:
            dump(data, _jsonFile, skipkeys=skipkeys, sort_keys=sort_keys, indent=indent, ensure_ascii=ensure_ascii)

    def appendFile(self, data: Union[list, dict[str, Any]], *, ensure_ascii: bool = False):
        concat_data(
            lambda _data: self.writeFile(_data, ensure_ascii=ensure_ascii),
            self.readFile(),
            data)
