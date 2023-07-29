from quicksort import test
import unittest
from datetime import datetime

class TestQuicksort(unittest.TestCase):
    def test_1(self):
        tick = datetime.now()
        self.assertEqual(test([1, 7, 4, 1, 10, 9, -2]), [-2, 1, 1, 4, 7, 9, 10])
        tock = datetime.now()
        diff = tock - tick
        print("Test 1 time:", str(diff.microseconds / 1000), "ms")
    def test_2(self):
        tick = datetime.now()
        self.assertEqual(test([-5, -6, 0, -7, -8, 10, 9, 16]), [-8, -7, -6, -5, 0, 9, 10, 16])
        tock = datetime.now()
        diff = tock - tick
        print("Test 2 time:", str(diff.microseconds / 1000), "ms")
    def test_3(self):
        tick = datetime.now()
        self.assertEqual(test([1, 1, 1]), [1, 1, 1])
        tock = datetime.now()
        diff = tock - tick
        print("Test 3 time:", str(diff.microseconds / 1000), "ms")
    def test_4(self):
        tick = datetime.now()
        self.assertEqual(test([9, 8, 7, 6, 5, 4, 3, 2, 1, 0]), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        tock = datetime.now()
        diff = tock - tick
        print("Test 4 time:", str(diff.microseconds / 1000), "ms")

if __name__ == '__main__':
    unittest.main()