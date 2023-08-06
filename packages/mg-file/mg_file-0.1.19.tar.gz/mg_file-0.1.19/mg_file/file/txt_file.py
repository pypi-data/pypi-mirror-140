__all__ = ["TxtFile"]

from typing import Dict, Union, Any, Literal, Optional

from .base_file import BaseFile


class TxtFile(BaseFile):
    """
    Работа с текстовым файлом

    :Example:

    .. code-block:: python

        from  mg_file.file.txt_file import TxtFile
        txt_obj = TxtFile('./path/file.txt')
    """

    def __init__(self, name_file: str, *,
                 mod: Optional[Literal['r', 'w', 'rb', 'wb', 'a', 'ab']] = None,
                 encoding: str = None,
                 data: Any = None,
                 type_file: Optional[str] = ".txt"):
        """
        Вы можете сразу выполнить метод указав ``mod``

        :param name_file:
        :param mod:
        :param encoding:
        :param data:
        :param type_file: Какое расширение должен иметь файл
        """
        super().__init__(name_file, type_file)
        if mod:
            self.res: Union[str, Any] = {
                "r": lambda: self.readFile(encoding=encoding),
                "w": lambda: self.writeFile(data=data),
                "rb": lambda: self.readBinaryFile(),
                "wb": lambda: self.writeBinaryFile(data=data),
                "a": lambda: self.appendFile(data=data),
                "ab": lambda: self.appendBinaryFile(data=data)
            }[mod]()

    def readFile(self, limit: int = 0, *, encoding: str = None) -> str:
        """
        Прочитать файл с начало

        :param limit: Ограничение чтения строк
        :param encoding: Кодировка
        """
        with open(self.name_file, "r", encoding=encoding) as f:
            if limit:
                res: str = ""
                for line in f:
                    if limit:
                        res += line
                        limit -= 1
                    else:
                        break
                return res
            else:
                return f.read()

    def readFileToResDict(self, *args: str, separator: str = '\n') -> Dict[str, str]:
        """
        Прочитать файл и вернуть словарь

        :param separator: Разделитель
        :param args: Имя ключей словаря

        :Пример:

        Файл ``./path/file.txt``

        .. code-block:: txt

            denisxab
            denis-k@mail.com
            password123

        Код

        .. code-block:: python

            from  mg_file.file.txt_file import TxtFile
            TxtFile('./path/file.txt').readFileToResDict("user_name","email","password")
            # {'user_name': 'denisxab', 'email': 'denis-k@mail.com', 'password': 'password123'}
        """
        resDict: Dict[str, str] = {}
        with open(self.name_file, "r") as f:
            for index, line in enumerate(f):
                resDict[args[index]] = line.replace(separator, "")
        return resDict

    def search(self, name_find: str) -> bool:
        """
        Простой поиск на соответствие тексту в файле

        :param name_find: Что искать

        :Пример:

        Файл ``./path/file.txt``

        .. code-block:: txt

            Optional. If the number of
            bytes returned exceed the hint number,
            no more lines will be returned. Default value is  -1,
            which means all lines will be returned.

        Код

        .. code-block:: python

            from  mg_file.file.txt_file import TxtFile
            TxtFile('./path/file.txt').searchFile("Default")
            # True
            TxtFile('./path/file.txt').searchFile("БУКВА")
            # False
        """
        res: bool = False
        with open(self.name_file, "r") as f:
            for line in f:
                if line.find(name_find) != -1:
                    res = True
                    break
        return res

    def readBinaryFile(self) -> bytes:  # +
        """
        Прочитать файл в бинарном режиме
        """
        with open(self.name_file, "rb") as f:
            return f.read()

    def writeFile(self, data: str):
        with open(self.name_file, "w") as f:
            f.write(data)

    def writeBinaryFile(self, data: Union[bytes, memoryview]):
        """
        Записать данные в бинарном режиме
        """
        with open(self.name_file, "wb") as f:
            f.write(data)

    def appendFile(self, data: str):  # +
        with open(self.name_file, "a") as f:
            f.write(data)

    def appendBinaryFile(self, data: bytes):
        """
        Добавить данные в бинарном режиме
        """
        with open(self.name_file, "ab") as f:
            f.write(data)
