import pytest

from mg_file import logger, loglevel, CompressionLog, LogFile
from mg_file.file.zip_file import ZippFile

file_name = "./test.log"


class TestCompressionLog:

    def setup(self):  # Выполнятся перед вызовом каждого метода

        ...

    @pytest.mark.parametrize(
        ('_loger', "_len"),
        [
            (loglevel('TEST',
                      file_name,
                      console_out=False,
                      max_size_file=30,
                      compression=CompressionLog.rewrite_file),
             90,
             ),
            (loglevel('TEST',
                      file_name,
                      console_out=False,
                      max_size_file=30,
                      compression=CompressionLog.zip_file),
             90,
             )
        ]
    )
    def test_compression(self, _loger, _len):
        """
        Проверка компрессии

        :param _loger:
        :param _len:
        """
        logger.test = _loger
        _f = LogFile(file_name)
        _f.deleteFile()
        for x in range(_len):
            logger.test(str(x))
        assert _f.readFile() == "TEST[]:88\nTEST[]:89\n"
        assert _f.sizeFile() == 20
        _f.deleteFile()
        ZippFile(f"{file_name}.zip").deleteFile()

    def teardown(self):  # Выполнятся после **успешного** выполнения каждого теста
        ...

    def __del__(self):  # Деструктор класса
        ...
