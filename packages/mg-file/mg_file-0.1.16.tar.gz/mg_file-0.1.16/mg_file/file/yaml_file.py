__all__ = ["YamlFile"]

from typing import Any, Union, Iterator, Optional

try:
    from yaml import load, Loader, dump, load_all
    from yaml.composer import ComposerError
except ImportError:
    ...

from .base_file import BaseFile, concat_data


class YamlFile(BaseFile):
    """
    Класс для работы с ``Yaml`` файлами
    """

    def __init__(self, name_file: str, type_file: Optional[str] = ".yaml"):
        super().__init__(name_file, type_file=type_file)

    def readFile(self,
                 *,
                 encoding: str = "utf-8",
                 _Loader=Loader,
                 limit: int = 0
                 ) -> Union[list, dict, Any]:
        """
        :param encoding: Кодировка
        :param _Loader: Разрешение чтение данных, которые хранятся в касторном типе.
        :param limit: Если в файле есть документ, то можно указать сколько документов нужно прочитать. -1 пропитать
            все документы из файла
        """

        def __read_all(__yamlFile):
            _reader: Iterator = load_all(_yamlFile, Loader=_Loader)
            return [_x for _x in _reader]

        with open(self.name_file, "r", encoding=encoding) as _yamlFile:
            _res: Union[list, dict, Any] = []

            if limit == 0:  # Если нужно прочитать весь файл, в котором нет документов.

                try:
                    _res = load(_yamlFile, Loader=_Loader)
                except ComposerError:  # Если в файле есть несколько документов, то читаем все документы.
                    _yamlFile.seek(0)  # Так как мы уже прочитали весь файл, то нам нужно вернутся в начало файла.
                    _res = __read_all(_yamlFile)

            elif limit > 0:  # Если в файле есть документы, и нам нужно прочитать определенное количество документов.
                reader = load_all(_yamlFile, Loader=_Loader)
                for _index, _row in enumerate(reader):
                    if _index < limit:
                        _res.append(_row)
                    else:
                        break
            else:  # Если в файле есть документы и нам нужно прочитать все документы.
                _res = __read_all(_yamlFile)

        return _res

    def writeFile(self,
                  data: Union[list, dict, Any],
                  *,
                  encoding: str = "utf-8",
                  default_flow_style: bool = False,
                  allow_unicode=True,
                  ):
        """
        :param data:
        :param encoding: Кодировка
        :param default_flow_style: 	Если вы хотите, чтобы коллекции всегда сериализовались
            в блочном стиле установите False
        :param allow_unicode:Экранировать символы, если True данные запишутся как есть.
        """
        with open(self.name_file, "w", encoding=encoding) as _yamlFile:
            dump(data, _yamlFile, default_flow_style=default_flow_style, allow_unicode=allow_unicode)

    def appendFile(self, data: Union[list, dict, Any], *,
                   encoding: str = "utf-8",
                   default_flow_style: bool = False,
                   allow_unicode=True, ):
        """Добавить данные в файл"""
        concat_data(
            lambda _data: self.writeFile(_data,
                                         default_flow_style=default_flow_style,
                                         encoding=encoding,
                                         allow_unicode=allow_unicode),
            self.readFile(),
            data)
