__all__ = ["PickleFile"]

from pickle import load, dump
from typing import Any, Union, Optional

from .base_file import BaseFile, concat_data


class PickleFile(BaseFile):
    """
    Работа с сериализоваными данными


    `Документация pickle
    <https://docs.python.org/3/library/pickle.html>`_

    """

    def __init__(self, name_file: str, type_file: Optional[str] = ".pkl"):
        super().__init__(name_file, type_file=type_file)

    def writeFile(self, data: Any, *, protocol: int = 3):
        """Сериализовать и записать данные в файл"""
        with open(self.name_file, "wb") as _pickFile:
            dump(data, _pickFile, protocol=protocol)

    def readFile(self, **kwargs) -> Any:
        """Прочитать и десериализация данные из файла"""
        with open(self.name_file, "rb") as _pickFile:
            return load(_pickFile)

    def appendFile(self, data: Union[tuple, list, dict, set], *, protocol: int = 3):
        concat_data(
            lambda _data: self.writeFile(_data, protocol=protocol),
            self.readFile(),
            data)
