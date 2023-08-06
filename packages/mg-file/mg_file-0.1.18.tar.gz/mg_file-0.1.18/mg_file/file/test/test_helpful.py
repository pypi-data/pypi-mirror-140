import doctest
import unittest

from mg_file.file import helpful


def load_tests(loader, tests, ignore):
    """
    Док тест
    """
    tests.addTests(doctest.DocTestSuite(helpful))
    return tests


if __name__ == '__main__':
    unittest.main()
