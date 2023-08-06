import unittest
from mp_complex import *


class MyTestCase(unittest.TestCase):
    def test_add_01(self):
        a: MPComplex = MPComplex(5, 3)
        b: MPComplex = MPComplex(7, 2)
        c: MPComplex = a + b
        self.assertEquals(c, MPComplex(12, 5))

    def test_add_02(self):
        a: MPComplex = MPComplex(5, -3)
        b: MPComplex = MPComplex(2, 5)
        c: MPComplex = a + b
        self.assertEquals(c, MPComplex(7, 2))

    def test_add_03(self):
        a: MPComplex = MPComplex(5, 3)
        b: mpf = mpf("18")
        c: MPComplex = a + b
        self.assertEquals(c, MPComplex(23, 3))

    def test_sub_01(self):
        a: MPComplex = MPComplex(5, 3)
        b: MPComplex = MPComplex(7, 2)
        c: MPComplex = a - b
        self.assertEquals(c, MPComplex(-2, 1))

    def test_sub_02(self):
        a: MPComplex = MPComplex(5, -3)
        b: MPComplex = MPComplex(2, 5)
        c: MPComplex = a - b
        self.assertEquals(c, MPComplex(3, -8))

    def test_sub_03(self):
        a: MPComplex = MPComplex(5, 3)
        b: mpf = mpf("18")
        c: MPComplex = a - b
        self.assertEquals(c, MPComplex(-13, 3))

    def test_mul_01(self):
        a: MPComplex = MPComplex(7, 3)
        b: MPComplex = MPComplex(2, 5)
        c: MPComplex = a * b
        self.assertEquals(c, MPComplex(-1, 41))

    def test_mul_02(self):
        a: MPComplex = MPComplex(-3, 3)
        b: MPComplex = MPComplex(-6, 5)
        c: MPComplex = a * b
        self.assertEquals(c, MPComplex(3, -33))

    def test_mul_03(self):
        a: MPComplex = MPComplex(3, -3)
        b: MPComplex = MPComplex(-6, 5)
        c: MPComplex = a * b
        self.assertEquals(c, MPComplex(-3, 33))

    def test_mul_04(self):
        a: MPComplex = MPComplex(3, -3)
        b: mpf = mpf("5")
        c: MPComplex = a * b
        self.assertEquals(c, MPComplex(15, -15))

    def test_div_01(self):
        a: MPComplex = MPComplex(7, 3)
        b: MPComplex = MPComplex(2, 5)
        c: MPComplex = a / b
        self.assertEquals(c, MPComplex(1, -1))

    def test_div_02(self):
        a: MPComplex = MPComplex(-7, 3)
        b: MPComplex = MPComplex(-2, 5)
        c: MPComplex = a / b
        self.assertEquals(c, MPComplex(1, 1))

    def test_div_03(self):
        a: MPComplex = MPComplex(7, -3)
        b: MPComplex = MPComplex(-2, 5)
        c: MPComplex = a / b
        self.assertEquals(c, MPComplex(-1, -1))

    def test_floordiv_01(self):
        a: MPComplex = MPComplex(7, 3)
        b: MPComplex = MPComplex(2, 5)
        c: MPComplex = a // b
        self.assertEquals(c, MPComplex(1, 0))

    def test_floordiv_02(self):
        a: MPComplex = MPComplex(-7, 3)
        b: MPComplex = MPComplex(-2, 5)
        c: MPComplex = a // b
        self.assertEquals(c, MPComplex(1, 0))

    def test_floordiv_03(self):
        a: MPComplex = MPComplex(7, -3)
        b: MPComplex = MPComplex(-2, 5)
        c: MPComplex = a // b
        self.assertEquals(c, MPComplex(-1, 0))

    def test_div_04(self):
        a: MPComplex = MPComplex(3, -3)
        b: mpf = mpf("5")
        c: MPComplex = a / b
        self.assertEquals(c, MPComplex(mpf("0.6"), mpf("-0.6")))

    def test_neg(self):
        a: MPComplex = MPComplex(33, 72)
        b: MPComplex = -a
        self.assertEquals(b, MPComplex(-33, -72))

    def test_pow(self):
        a: MPComplex = MPComplex(3, 3)
        b: MPComplex = a ** 5
        self.assertEquals(b, MPComplex(-972, -972))

    def test_comparisons(self):
        self.assertTrue(MPComplex(5, 3) > mpf("5"))
        self.assertTrue(MPComplex(5, 0) >= mpf("5"))
        self.assertTrue(MPComplex(5, 0) == mpf("5"))
        self.assertTrue(MPComplex(5, -3) <= mpf("5"))
        self.assertTrue(MPComplex(5, -3) < mpf("5"))
        self.assertTrue(MPComplex(3, 7) == MPComplex(3, 7))
        self.assertTrue(MPComplex(3, 7) != MPComplex(3, 6))
        self.assertTrue(MPComplex(3, 7) != MPComplex(6, 7))
        self.assertTrue(MPComplex(3, 7) != MPComplex(6, 2))
        self.assertTrue(MPComplex(3, 7) > MPComplex(2, 5))
        self.assertTrue(MPComplex(3, 7) > MPComplex(3, 5))
        self.assertTrue(MPComplex(3, 7) >= MPComplex(2, 5))
        self.assertTrue(MPComplex(3, 7) >= MPComplex(3, 5))
        self.assertTrue(MPComplex(1, 7) < MPComplex(2, 5))
        self.assertTrue(MPComplex(1, 7) < MPComplex(1, 15))
        self.assertTrue(MPComplex(1, 7) <= MPComplex(2, 5))
        self.assertTrue(MPComplex(1, 7) <= MPComplex(1, 15))

    def test_sort_list(self):
        a_list: list = [MPComplex(5, 2), MPComplex(6, 3), MPComplex(2, 7)]
        a_list.sort()
        self.assertEquals(a_list, [MPComplex(2, 7), MPComplex(5, 2), MPComplex(6, 3)])


if __name__ == '__main__':
    unittest.main()
