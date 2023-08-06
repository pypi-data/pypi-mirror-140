from typing import Optional, Any, Literal

from .txt_file import TxtFile


class LogFile(TxtFile):
    """
    Класс дял работы с лог файлами
    """

    def __init__(self, name_file: str, *, mod: Optional[Literal['r', 'w', 'rb', 'wb', 'a', 'ab']] = None,
                 encoding: str = None, data: Any = None, type_file: Optional[str] = ".log"):
        super().__init__(name_file, mod=mod, encoding=encoding, data=data, type_file=type_file)
