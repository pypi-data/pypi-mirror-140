from abc import abstractmethod
from os import makedirs, remove, mkdir
from os.path import abspath, dirname, exists, getsize, splitext
from pickle import load, dump
from shutil import rmtree
from typing import Any, Callable, TypeAlias, Union, Optional

from .base_crypto import CryptoAes, SecretDataAes
from .helpful import sha256sum


class BaseFile:
    """
    Базовый класс для файлов
    """
    __slots__ = "name_file"

    def __init__(self, name_file: str, type_file: Optional[str]):
        """
        :param type_file: Какое расширение должен иметь файл. Если указать
            None то это значит что проверка попуститься
        :param name_file: Путь к файлу
        """
        self.check_extensions_file(name_file, type_file)
        self.name_file: str = name_file  #: Путь к файлу
        self.createFileIfDoesntExist()

    @staticmethod
    def check_extensions_file(name_file: str, req_type: str):
        """
        Проверить расширение файла

        :param name_file: Путь к файлу
        :param req_type: Требуемое расширение
        """
        # Если не нужно проверять имя расширения
        if not req_type:
            return
        if splitext(name_file)[1] != req_type:  # Проверяем расширение файла
            raise ValueError(f"Файл должен иметь расширение {req_type}")

    def createFileIfDoesntExist(self):
        """
        Создать файл если его нет
        """
        if not exists(self.name_file):
            tmp_ = dirname(self.name_file)
            if tmp_ and not exists(tmp_):  # Если задан путь из папок если их нет
                makedirs(tmp_)  # Создаем путь из папок
                open(self.name_file, "w").close()
            else:
                # Если указано только имя файла без папок
                # или папки же существуют
                open(self.name_file, "w").close()

    def checkExistenceFile(self) -> bool:  # +
        """
        Проверить существование файла
        """
        return True if exists(self.name_file) else False

    def deleteFile(self):  # +
        """
        Удалить файл
        """
        # Удаление файла
        if self.checkExistenceFile():
            remove(self.route())

    def sizeFile(self) -> int:  # +
        """
        Получить размер файла
        """
        # Размер файла в байтах
        return getsize(self.name_file)

    def route(self) -> str:  # +
        """
        Получить абсолютный путь
        """
        # Путь к файлу
        return abspath(self.name_file)

    def createRoute(self):
        """
        Создать файл по указному пути, если нужно поместить в папки, то они создадутся
        """
        tmp_route: str = ""
        for folder_name in self.name_file.split('/')[:-1]:
            tmp_route += folder_name
            mkdir(tmp_route)
            tmp_route += '/'

    def removeRoute(self):
        """
        Удалить весь путь к файлу
        """
        rmtree(self.name_file.split('/')[1])

    def hashFileSha256(self) -> str:
        """
        Получить хеш сумму файла
        """
        return sha256sum(self.name_file)

    def encryptFile(self, key: str, outpath: Optional[str] = str):
        """
        Зашифровать файл

        :param key: Ключ для шифрования, должен иметь длину 16,24,32 байта
        :param outpath: Путь куда сохранить зашифрованный файл
        """
        res: SecretDataAes = CryptoAes(key).encodeAES(str(self.readFile()))
        with open(outpath if outpath else self.name_file, "wb") as _pickFile:
            dump(res, _pickFile, protocol=3)

    def decryptoFile(self, key: str) -> Optional[str]:
        """
        Расшифровать файл

        :param key: Ключ для шифрования, должен иметь длину 16,24,32 байта
        """
        with open(self.name_file, "rb") as _pickFile:
            return CryptoAes(key).decodeAES(load(_pickFile))

    @abstractmethod
    def readFile(self, *arg) -> Any:
        """
        Прочитать файл
        """
        ...

    @abstractmethod
    def writeFile(self, arg: Any):
        """
       Записать данные в файл
       """
        ...

    @abstractmethod
    def appendFile(self, arg: Any):
        """
        Добавить данные в файл
        """
        ...


T_ConcatData: TypeAlias = Union[list[Union[str, int, float]], list[list[Union[str, int, float]]], dict, set, str]


def concat_data(callback: Callable, file_data: T_ConcatData, new_data: T_ConcatData):
    """
    Объединить два переменных, если они одинакового типа

    :param callback: Вызовется при успешной проверки типов
    :param file_data: Данные из файле
    :param new_data: Текущие данные в `Python`
    """

    # Входные данные должны быть такого же типа, что и в файле
    if type(file_data) == type(new_data):
        match new_data:
            case list():
                file_data.extend(new_data)
            case tuple() | str():
                file_data += new_data
            case dict() | set():
                file_data.update(new_data)
            case _:
                raise TypeError("Не поддерживаемый тип")
        callback(file_data)
    else:
        raise TypeError("Тип данных в файле и тип входных данных различны")
