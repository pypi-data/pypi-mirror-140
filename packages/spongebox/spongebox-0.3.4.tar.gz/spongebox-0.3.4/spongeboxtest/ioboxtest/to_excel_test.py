import unittest
from spongebox.iobox import to_excel
import pandas as pd
import numpy as np


class MyTestCase(unittest.TestCase):
    def test_something(self):
        df1 = pd.DataFrame(np.random.randint(0, 6, (3, 3)), columns=list("abc"))
        df2 = pd.DataFrame(np.random.randint(0, 6, (3, 3)), columns=list("abc"))
        _ = {"df1": df1, "df2": df2}
        to_excel(_, "C:\\Users\\LuoJi\\Desktop\\test_toxls.xlsx")
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
