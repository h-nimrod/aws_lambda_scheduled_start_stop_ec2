# coding: utf-8

import unittest
import sys
sys.path.append('../')
import MyJST
import datetime



class TestSample(unittest.TestCase):
    def setUp(self):
        self.jst = MyJST.MyJST()

    def adjust(self, year, month, day, h):
        self.jst.jst_now = datetime.datetime(year, month, day, hour=h)

    def test_1(self):
        self.adjust(2017,1,1, 0) # 正月, 日曜日
        self.assertEqual(self.jst.is_holiday(), True, self.jst.get_jst_now())
        self.assertEqual(self.jst.is_weekday(), False, self.jst.get_jst_now())

    def test_2(self):
        self.adjust(2016,12,31, 0)
        self.assertEqual(self.jst.is_holiday(), False, self.jst.get_jst_now())

    def test_3(self):
        self.adjust(2017,4,3, 0)
        self.assertEqual(self.jst.is_holiday(), False, self.jst.get_jst_now())
        self.assertEqual(self.jst.is_weekday(), True, self.jst.get_jst_now())

    def test_4(self):
        self.adjust(2017,5,3, 0) # 憲法記念日, 水曜日
        self.assertEqual(self.jst.is_holiday(), True, self.jst.get_jst_now())
        self.assertEqual(self.jst.is_weekday(), False, self.jst.get_jst_now())



if __name__ == "__main__":
    unittest.main()
