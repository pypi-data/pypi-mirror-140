import os
import unittest
from pathlib import Path

import sswrap


class TestSswrap(unittest.TestCase):
    def test_csv(self):
        cells_path = Path(os.path.dirname(__file__)) / "files/cells.csv"
        ss = sswrap.load(cells_path)
        self.assertIsNotNone(ss)
        self.assertEqual(1, ss.num_worksheets())
        ws = ss[0]
        self.assertIsNotNone(ws)
        self.assertEqual("A1", ws.get_value(0, 0))
        self.assertEqual("A2", ws.get_value(1, 0))
        self.assertEqual("B1", ws.get_value(0, 1))
        self.assertEqual("B3", ws.get_value(2, 1))
        self.assertEqual("Z3", ws.get_value(2, 25))
