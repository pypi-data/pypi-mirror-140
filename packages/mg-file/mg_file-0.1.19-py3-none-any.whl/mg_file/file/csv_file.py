__all__ = ["CsvFile"]

from csv import reader, writer
from os import SEEK_END, SEEK_SET
from typing import Union, List, Callable, Optional

try:
    # pip install prettytable
    from prettytable import PrettyTable
except ImportError:
    ...

from .base_file import BaseFile, concat_data


class CsvFile(BaseFile):
    """
    Класс для работы csv файлами

    :Пример:

    .. code-block:: python

        from mg_file.file.csv_file import CsvFile

        csv_obj = CsvFile("./path/file.csv")

        csv_obj.writeFile(
            [[1, 23, 41, 5],
             [21, 233, 46, 35],
             [13, 233, 26, 45],
             [12, 213, 43, 56]], FlagDataConferToStr=True, header=("Данные", "Data", "Числа", "Num"))

        assert csv_obj.readFile() == [['Данные', 'Data', 'Числа', 'Num'],
                                      ['1', '23', '41', '5'],
                                      ['21', '233', '46', '35'],
                                      ['13', '233', '26', '45'],
                                      ['12', '213', '43', '56']]
    """

    def __init__(self, name_file: str, type_file: Optional[str] = ".csv"):
        super().__init__(name_file, type_file=type_file)

    def readFile(self,
                 *,
                 encoding: str = "utf-8",
                 limit: int = 0,
                 miss_get_head=False,
                 delimiter=",",
                 ) -> list[list[str]]:
        """
        Прочитать файл

        :param limit: Лимит чтения записей
        :param miss_get_head: Пропустить чтение заголовка
        :param delimiter: Символ, который будет разделять колонки
        :param encoding: Кодировка
        """
        _res: list[list[str]] = []
        with open(self.name_file, "r", encoding=encoding) as _csvFile:
            _reader = reader(_csvFile, delimiter=delimiter)

            if limit:  # Если есть лимит для чтения записей
                for _index, _row in enumerate(_reader):
                    if _index < limit:
                        _res.append(_row)
                    else:
                        break
            else:  # Если лимита нет, то читаем все записи
                _res = list(_reader)

            if miss_get_head:  # Если нужно пропустить заголовки
                return _res[1::]

            else:
                return _res

    def readFileAndFindDifferences(self, new_data_find: List[List], funIter: Callable) -> bool:  # +
        """
        Прочитать файл и найти различия

        :param new_data_find: Новые данные
        :param funIter: Функция, которая будет выполняться если строки не равны

        :Пример:

        .. code-block:: python

            from mg_file.file.csv_file import CsvFile
            csv_obj = CsvFile("./path/file.csv")

            data_file = [['1', '2'],
                         ['3', '2'],
                         ["today", "Saturday"]]

            new_data = [['1', '2'],
                        ['3', '2'],
                        ["today", "Monday"]]

            DifferenceList = []
            csv_obj.writeFile(data_file, header=("h1", "h2"))
            csv_obj.readFileAndFindDifferences(new_data, DifferenceList.append)
            assert DifferenceList == [["today", "Saturday"]]

        """
        data_file = self.readFile(miss_get_head=True)
        if data_file != new_data_find:
            """
            for new_data, data_file in zip(self.ListStock, DataFile):
                if new_data != data_file:
                    funIter(new_data)
            """
            for _ in (funIter(new_data)
                      for new_data in new_data_find
                      if new_data not in data_file):
                continue
            return True
        else:
            return False

    def readFileRevers(self, *,
                       limit: int = None,
                       encoding: str = "utf-8",
                       newline: str = ""
                       ) -> List[List[str]]:
        """
        Прочить файл в обратном порядке


        :Пример:

        .. code-block:: python

            from mg_file.file.csv_file import CsvFile
            csv_obj = CsvFile("./path/file.csv")

            csv_obj.writeFile(
                [[1, 23, 41, 5],
                 [21, 233, 46, 35],
                 [13, 233, 26, 45],
                 [12, 213, 43, 56]], FlagDataConferToStr=True, header=("Данные", "Data", "Числа", "Num"))

            assert csv_obj.readFileRevers() == [['12', '213', '43', '56'],
                                                ['13', '233', '26', '45'],
                                                ['21', '233', '46', '35'],
                                                ['1', '23', '41', '5'],
                                                ['Данные', 'Data', 'Числа', 'Num']]
        """

        def reversed_lines(file):
            # Generate the lines of file in reverse order
            part = ''
            for block in reversed_blocks(file):
                for c in reversed(block):
                    if c == '\n' and part:
                        yield part[::-1]
                        part = ''
                    part += c
            if part:
                yield part[::-1]

        def reversed_blocks(file, block_size=4096):
            # Generate blocks of file's contents in reverse order.
            file.seek(0, SEEK_END)
            here = file.tell()
            while 0 < here:
                delta = min(block_size, here)
                here -= delta
                file.seek(here, SEEK_SET)
                yield file.read(delta)

        res = []
        with open(self.name_file, "r", encoding=encoding, newline=newline) as f:

            if limit:  # Лимит чтения строк
                for row in reader(reversed_lines(f)):
                    if limit:
                        res.append(row)
                        limit -= 1
                    else:
                        break
            else:
                for row in reader(reversed_lines(f)):
                    res.append(row)
        return res

    def writeFile(self,
                  data: Union[list[Union[str, int, float]],
                              list[list[Union[str, int, float]]]],
                  *,
                  header: tuple = None,
                  FlagDataConferToStr: bool = False,
                  encoding: str = "utf-8",
                  delimiter=",",
                  newline="",
                  ):
        """
        :param data: Данные на запись
        :param header: Эти данные будут заголовками
        :param FlagDataConferToStr: Переводит все данные в формат str
        :param delimiter: Символ, который будет разделять колонки
        :param encoding: Кодировка
        :param newline:
        """
        with open(self.name_file, "w", encoding=encoding, newline=newline) as _csvFile:
            _writer = writer(_csvFile, delimiter=delimiter)

            if header:  # Запись заголовка
                _writer.writerow(header)

            if FlagDataConferToStr:
                if type(data[0]) != list:
                    data = [str(n) for n in data]
                else:
                    data = [[str(n) for n in m] for m in data
                            # Проверить что объект можно перебрать
                            if getattr(m, "__iter__", False)]

            if type(data[0]) != list:
                _writer.writerow(data)
            else:
                _writer.writerows(data)

    def appendFile(self, data: Union[list[Union[str, int, float]],
                                     list[list[Union[str, int, float]]]],
                   *,
                   FlagDataConferToStr: bool = False,
                   encoding: str = "utf-8",
                   delimiter=",",
                   ):
        """
        Добавить данные в файл

        :param data: Новые данные
        :param FlagDataConferToStr: Переводит все данные в формат str
        :param delimiter: Символ, который будет разделять колонки
        :param encoding: Кодировка

        :Пример:

        .. code-block:: python

            from mg_file.file.csv_file import CsvFile
            csv_obj = CsvFile("./path/file.csv")

            csv_obj.writeFile(
                [[1, 23, 41, 5],
                 [21, 233, 46, 35],
                 [13, 233, 26, 45],
                 [12, 213, 43, 56]], FlagDataConferToStr=True, header=("Данные", "Data", "Числа", "Num"))

            csv_obj.appendFile([['2323', '23233', '23']])

            assert csv_obj.readFile() == [['Данные', 'Data', 'Числа', 'Num'],
                                          ['1', '23', '41', '5'],
                                          ['21', '233', '46', '35'],
                                          ['13', '233', '26', '45'],
                                          ['12', '213', '43', '56'],
                                          ['2323', '23233', '23']]
        """
        concat_data(
            lambda _data: self.writeFile(_data,
                                         FlagDataConferToStr=FlagDataConferToStr,
                                         encoding=encoding,
                                         delimiter=delimiter),
            self.readFile(),
            data)

    @staticmethod
    def ptabel(data: list[list[str]], align="l") -> PrettyTable:
        """
        Вернуть список в виде красивой таблице


        :param data: Список данных
        :param align: Выравнивание

        .. note::
            Нужно иметь ``pip install prettytable``


        :Пример:

        .. code-block:: csv

            Данные,Data,Числа,Num
            1,23,41,5
            21,233,46,35
            13,233,26,45
            12,213,43,56

        .. code-block:: python

            from  mg_file.file.csv_file import CsvFile

            cvs_file = CsvFile('./path/file.csv')
            cvs_file.ptabel(cvs_file.readFile())

        :Вывод:

        .. code-block:: text

            +--------+------+-------+-----+
            | Данные | Data | Числа | Num |
            +--------+------+-------+-----+
            | 1      | 23   | 41    | 5   |
            | 21     | 233  | 46    | 35  |
            | 13     | 233  | 26    | 45  |
            | 12     | 213  | 43    | 56  |
            +--------+------+-------+-----+
        """
        x = PrettyTable(data[0])
        x.add_rows(data[1:])
        x.align = align
        return x
