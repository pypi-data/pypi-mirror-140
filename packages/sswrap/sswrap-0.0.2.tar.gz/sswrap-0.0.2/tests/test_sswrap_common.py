import unittest

import sswrap.common


class TestSswrapCommon(unittest.TestCase):
    def test_to_a1_cell(self):
        self.assertEqual("A1", sswrap.common.to_a1_cell(0, 0))
        self.assertEqual("A26", sswrap.common.to_a1_cell(25, 0))
        self.assertEqual("AA25", sswrap.common.to_a1_cell(24, 26))
        self.assertEqual("AA25", sswrap.common.to_a1_cell(24, 26))
        self.assertEqual("ZZ702", sswrap.common.to_a1_cell(701, 701))
        self.assertEqual("AAA703", sswrap.common.to_a1_cell(702, 702))

    def test_from_a1_cell(self):
        self.assertEqual((0, 0), sswrap.common.from_a1_cell("A1"))
        self.assertEqual((25, 0), sswrap.common.from_a1_cell("A26"))
        self.assertEqual((24, 26), sswrap.common.from_a1_cell("AA25"))
        self.assertEqual((702, 702), sswrap.common.from_a1_cell("AAA703"))
