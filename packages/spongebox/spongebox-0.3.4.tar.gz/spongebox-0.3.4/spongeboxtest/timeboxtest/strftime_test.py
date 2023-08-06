import unittest
from spongebox.timebox import strptime, strftime


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual("2020-01-01 00:00:00",strftime(strptime(20200101)))  # add assertion here
        self.assertEqual("20200101",strftime(strptime(20200101), "%Y%m%d"))  # add assertion here


if __name__ == '__main__':
    unittest.main()
