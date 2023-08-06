import unittest
from spongebox.iobox import mk_dir


class MyTestCase(unittest.TestCase):
    def test_something(self):
        mk_dir("C:\\Users\\LuoJi\\Desktop\\data1")
        mk_dir("C:\\Users\\LuoJi\\Desktop\\data2")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
