from mg_file import TxtFile

file_name = "./test.txt"
file_name_out = "./test_crp.txt"
secret_key = "Sixteen byte kys"
data = "Привет мир ВОт мои dAta 123"


class Test_BaseFile:

    def setup(self):  # Выполнятся перед вызовом каждого метода
        ...

    def test_encryptFile(self):  # Все методы должны начинаться со слова `test_`
        _f = TxtFile(file_name)
        _f.writeFile(data)
        _f.encryptFile(secret_key, file_name_out)
        res = TxtFile(file_name_out).decryptoFile(secret_key)
        assert res == data
        _f.deleteFile()
        TxtFile(file_name_out).deleteFile()

    def teardown(self):  # Выполнятся после **успешного** выполнения каждого теста
        ...

    def __del__(self):  # Деструктор класса
        ...
