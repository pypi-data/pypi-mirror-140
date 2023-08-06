__all__ = ["BaseFolder", "Folder", "TgetAllFileAndFolder", "DiffDir"]

from collections import deque
from os import sep, listdir, path
from re import match
from typing import NamedTuple, Union, TypedDict, Optional

from .base_file import sha256sum


class DiffDir(NamedTuple):
    """
    Объект для хранения разницы меду двумя директориями
    """
    #: Текущая директория (А)
    infloder: str
    #: Сравнительная директория (Б)
    outfolder: str
    #: Файлы, которые не существую в директории (Б)
    not_exist_arr_file: set[str]
    #: Папки, которые не существуют в директории (Б)
    not_exist_arr_folder: set[str]
    #: Данные в (Б) отличаются от данных в (А)
    diff_data_arr_file: set[str]
    #: Файлы, которые нарушают исключение и существуют в (Б)
    file_intruder: set[str]
    #: Папки, которые нарушают исключение и существуют в (Б)
    folder_intruder: set[str]

    # def log(self):
    #     logger.info(f"NotFile:\n{pformat(self.not_exist_arr_file)}")
    #     logger.info(f"NotFolder:\n{pformat(self.not_exist_arr_folder)}")
    #     logger.info(f"DiffHashFile:\n{pformat(self.diff_data_arr_file)}")
    #     logger.info(f"FileIntruder:\n{pformat(self.file_intruder)}")
    #     logger.info(f"FolderIntruder:\n{pformat(self.folder_intruder)}")


class TgetAllFileAndFolder(TypedDict):
    """
    Тип для :meth:`file.base_folder.BaseFolder.getAllFileAndFolder`
    """
    split_path: str  #: Начало которое нужно отделить от путей
    arr_file: set[str]  #: Список файлов
    arr_folder: set[str]  #: Список папок


class BaseFolder:
    """
    Базовый класс для работы с директориями
    """

    def __init__(self, folder: str, arr_exclude: Optional[set[str]] = None):
        """
        :param folder: Директория из которой нужно получить файлы и папки
        :param arr_exclude: Пути которые нужно исключить
        """
        self.folder: str = folder
        self.arr_exclude: set[str] = arr_exclude if arr_exclude else set()

    def getAllFileAndFolder(self) -> TgetAllFileAndFolder:
        """
        Получить список всех файлов и папок по указному пути.
        """

        arr_file: set[str] = set()  #: Список со всеми файлами
        arr_folder: set[str] = set()  #: Список со всеми папками
        ###################################
        # Изначальный путь к папке
        _path: str = self.folder
        # Временный список с папками для перебора
        _arr_select_folder: deque = deque([self.folder])
        _Live = True
        while _Live:
            # Выбираем первый элемент путь из очереди
            _path = _arr_select_folder[0]
            # Перебираем все файлы и папки в пути
            for x in listdir(_path):
                # Создаем полный путь
                file = path.join(_path, x)
                # Если папка
                if path.isdir(file):
                    # Добавляем в результирующий массив
                    # Если имя переименовали то создаем объект `TypeReplaceName
                    arr_folder.add(file.replace(self.folder, ''))
                    # Добавляем в список перебора путей
                    _arr_select_folder.append(file)
                # Если файл
                else:
                    # Добавляем в результирующий список файлов
                    # Если имя переименовали то создаем объект `TypeReplaceName
                    arr_file.add(file.replace(self.folder, ''))
            # Удаляем путь, который перебрали
            _arr_select_folder.popleft()
            # Если путей нет, то прекращаем перебор
            if len(_arr_select_folder) == 0:
                _Live = False

        return TgetAllFileAndFolder(
            split_path=self.folder,
            arr_file=arr_file,
            arr_folder=arr_folder
        )

    def excludeFolderAndFile(self,
                             arr_file: set[str],
                             arr_folder: set[str], **kwargs) \
            -> tuple[set[str], set[str]]:
        """
        Метод для исключения фалов и папок из списков.

        :param arr_file: Список файлов
        :param arr_folder: Список папок
        :return: Новый список файлов и папок, с исключенными путями
        """

        # Если нечего исключать, то возвращаем исходные данные
        if not self.arr_exclude:
            return arr_file, arr_folder

        def isExclude(_path: str) -> bool:
            # Проверяем путь на вхождение в список исключений
            for _re in self.arr_exclude:
                # Проверяем начло не соответствие шаблону исключения
                isExist = match(fr"{_re}[\W\w]*", _path.__str__())
                if isExist:
                    return True
            return False

        def logic(_arr_path) -> set[str]:
            _right_path: set[str] = set()
            # Перебираем пути
            for _path in _arr_path:
                # Если путь НЕ нужно исключить, то добавляем его в правильный путь
                if not isExclude(_path):
                    _right_path.add(_path)
            return _right_path

        return logic(arr_file), logic(arr_folder)

    @staticmethod
    def sortPath(arr_path: Union[list[str], set[str]], reverse: bool = True) -> list[str]:
        """
        Отсортировать пути.
        Для создания и удаления папок необходимо соблюдать порядок путей.

        :param arr_path: Список путей
        :param reverse: Сортировать в обратном порядке.
         Сначала длинный путь, который будет указывать на файл, в конце, короткий путь,
         который будет указывать на папку. Когда мы будем удалять файлы и папки то нам
         нужно отсортировать пути в обратном порядке. Когда нам нужно создать файлы и папки то
         нам нужен обычный порядок.
        """
        # Создаем список с количеством разделителей директорий
        _res: list[tuple[int, str]] = [(len(_x.split(sep)), _x) for _x in list(arr_path)]
        # Сортируем директории по количеству разделителей, в обратном порядке
        _res.sort(key=lambda k: k[0], reverse=reverse)
        # Преобразуем данные
        _res: list[str] = [_x[1] for _x in _res]
        return _res


class Folder(BaseFolder):
    """
    Работа с директориями
    """

    @staticmethod
    def _dirDiff(
            in_folder: str,
            arr_file_in: set[str], arr_folder_in: set[str],
            outfolder: str,
            arr_file_out: set[str], arr_folder_out: set[str],
    ) -> DiffDir:
        """
        Метод для получения разницы между директориями.
        Проверка не пройдена если:
        - Файла или директории не существует
        - Файл имеют разные хеш суммы
        - Файл или папка которая находиться в исключение, но существует в Б

        :param in_folder: Текущая директория (А)
        :param arr_file_in: Список файлов в текущей директории
        :param arr_folder_in: Список папок в текущей директории

        :param outfolder: Сравнительная директория (Б)
        :param arr_file_out: Список файлов в текущей сравнительной директории
        :param arr_folder_out: Список папок в текущей сравнительной директории

        :return: Список директорий и файлов который нужно скопировать
        """

        def FolderIfNotExist() -> set[str]:
            """
            Получить список папок которых нет в Б директории
            """
            _res_f = set()
            for _path in arr_folder_in:
                _out_path = f"{outfolder}{_path}"
                if not path.isdir(_out_path):
                    _res_f.add(_path)
            return _res_f

        def FileIfChangeDataOrNotExist() -> tuple[set[str], set[str]]:
            """
            Скопировать файл если его нет или, у них различная хеш сумма
            """
            _diff_data_arr_file = set()
            _not_exist_arr_file = set()
            for _path in arr_file_in:
                _in_path = f"{in_folder}{_path}"
                _out_path = f"{outfolder}{_path}"
                # Если файла нет, то копируем его
                if not path.isfile(_out_path):
                    _not_exist_arr_file.add(_path)
                # Если файл уже есть, то проверим его хеш
                else:
                    # Если хеш одинаковый, то не копируем файл
                    # Если хеш разный, то копируем файл
                    if sha256sum(_in_path) != sha256sum(_out_path):
                        _diff_data_arr_file.add(_path)

            return _diff_data_arr_file, _not_exist_arr_file

        """
        Получаем данные о директории А
        """
        # Файлы, которые имеют разную хеш сумму. Файлы которых есть в А, но нет в Б
        diff_data_arr_file, not_exist_arr_file = FileIfChangeDataOrNotExist()
        # Папки которых есть в А, но нет в Б
        not_exist_arr_folder: set[str] = FolderIfNotExist()

        """
        Получаем данные о директории Б 
        """
        # Файлы, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        file_intruder: set[str] = arr_file_out.difference(arr_file_in)
        # Папки, которые существуют только в Б.
        # Это может происходить если мы добавили в исключение файл которые ранее в нем не был.
        folder_intruder: set[str] = arr_folder_out.difference(arr_folder_in)
        _res = DiffDir(in_folder, outfolder,
                       not_exist_arr_file,
                       not_exist_arr_folder,
                       diff_data_arr_file,
                       file_intruder,
                       folder_intruder)
        return _res

    def getDiff(self, folder_two: BaseFolder) -> DiffDir:
        """
        Получить различия между дирекцией А и Б

        А - директория откуда брать данные
        Б - директория куда копировать данные

        :param folder_two: директория с которой нужно сравнить
        """
        # Получаем пути к файлам и папкам из директории А
        arr_file_in, arr_folder_in = self.excludeFolderAndFile(self.arr_exclude,
                                                               **self.getAllFileAndFolder())
        # Получаем пути к файлам и папкам из директории Б
        arr_file_out, arr_folder_out = folder_two.excludeFolderAndFile(folder_two.arr_exclude,
                                                                       **folder_two.getAllFileAndFolder())

        # logger.debug(
        #     "Tracking:\n{0}".format(pformat(
        #         {'arr_file_in': arr_file_in,
        #          'arr_folder_in': arr_folder_in,
        #          'arr_file_out': arr_file_out,
        #          'arr_folder_out': arr_folder_out}, compact=True)))

        # Получим разницу между А и Б директориями
        return self._dirDiff(
            self.folder,
            arr_file_in, arr_folder_in,
            folder_two.folder,
            arr_file_out, arr_folder_out,
        )
