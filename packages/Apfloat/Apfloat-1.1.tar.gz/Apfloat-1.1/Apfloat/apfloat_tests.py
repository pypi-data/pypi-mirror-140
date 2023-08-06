import unittest
from apfloat import *


class MyTestCase(unittest.TestCase):
    def test_add_01(self):
        a: Apfloat = Apfloat("55")
        b: Apfloat = Apfloat("77")
        c: Apfloat = a + b
        self.assertEquals(c, Apfloat("132"))

    def test_add_02(self):
        a: Apfloat = Apfloat("55")
        b: Apfloat = Apfloat("-77")
        c: Apfloat = a + b
        self.assertEquals(c, Apfloat("-22"))

    def test_add_03(self):
        a: Apfloat = Apfloat("5.13")
        b: Apfloat = Apfloat("7.12")
        c: Apfloat = a + b
        self.assertEquals(c, Apfloat("12.25"))

    def test_sub_01(self):
        a: Apfloat = Apfloat("55")
        b: Apfloat = Apfloat("77")
        c: Apfloat = a - b
        self.assertEquals(c, Apfloat("-22"))

    def test_sub_02(self):
        a: Apfloat = Apfloat("55")
        b: Apfloat = Apfloat("-77")
        c: Apfloat = a - b
        self.assertEquals(c, Apfloat("132"))

    def test_sub_03(self):
        a: Apfloat = Apfloat("9.33")
        b: Apfloat = Apfloat("5.22")
        c: Apfloat = a - b
        self.assertEquals(c, Apfloat("4.11"))

    def test_mul_01(self):
        a: Apfloat = Apfloat("77")
        b: Apfloat = Apfloat("12")
        c: Apfloat = a * b
        self.assertEquals(c, Apfloat("924"))

    def test_mul_02(self):
        a: Apfloat = Apfloat("77")
        b: Apfloat = Apfloat("-12")
        c: Apfloat = a * b
        self.assertEquals(c, Apfloat("-924"))

    def test_mul_03(self):
        a: Apfloat = Apfloat("3.14")
        b: Apfloat = Apfloat("4.16")
        c: Apfloat = a * b
        self.assertEquals(c, Apfloat("13.0624"))

    def test_div_01(self):
        a: Apfloat = Apfloat("87")
        b: Apfloat = Apfloat("12")
        c: Apfloat = a / b
        self.assertEquals(c, Apfloat("7.25"))

    def test_div_02(self):
        a: Apfloat = Apfloat("87")
        b: Apfloat = Apfloat("-12")
        c: Apfloat = a / b
        self.assertEquals(c, Apfloat("-7.25"))

    def test_div_03(self):
        a: Apfloat = Apfloat("7.85")
        b: Apfloat = Apfloat("3.14")
        c: Apfloat = a / b
        self.assertEquals(c, Apfloat("2.5"))

    def test_floordiv_01(self):
        a: Apfloat = Apfloat("87")
        b: Apfloat = Apfloat("12")
        c: Apfloat = a // b
        self.assertEquals(c, Apfloat("7"))

    def test_floordiv_02(self):
        a: Apfloat = Apfloat("87")
        b: Apfloat = Apfloat("-12")
        c: Apfloat = a // b
        self.assertEquals(c, Apfloat("-8"))

    def test_floordiv_03(self):
        a: Apfloat = Apfloat("7.85")
        b: Apfloat = Apfloat("3.14")
        c: Apfloat = a // b
        self.assertEquals(c, Apfloat("2"))

    def test_pos(self):
        a: Apfloat = Apfloat("5.3")
        self.assertEquals(a, a.__pos__())

    def test_neg(self):
        a: Apfloat = Apfloat("5.3")
        b: Apfloat = a.__neg__()
        self.assertEquals(b, Apfloat("-5.3"))

    def test_pow_01(self):
        a: Apfloat = Apfloat("3")
        b: Apfloat = a ** 5
        self.assertEquals(b, Apfloat("243"))

    def test_pow_02(self):
        a: Apfloat = Apfloat("4")
        b: Apfloat = a ** Apfloat("2.5")
        self.assertEquals(b, Apfloat("32"))

    def test_comparisons(self):
        self.assertTrue(Apfloat("5") > Apfloat("3"))
        self.assertTrue(Apfloat("5") >= Apfloat("3"))
        self.assertTrue(Apfloat("5") == Apfloat("5.00"))
        self.assertTrue(Apfloat("5") != Apfloat("5.0000001"))
        self.assertTrue(Apfloat("2.77") < Apfloat("3"))
        self.assertTrue(Apfloat("2.77") <= Apfloat("3"))

    def test_sort_list(self):
        a_list: list = [Apfloat("2.77"), Apfloat("9.43"), Apfloat("5.22"), Apfloat("-3.13")]
        a_list.sort()
        self.assertEquals(a_list, [Apfloat("-3.13"), Apfloat("2.77"), Apfloat("5.22"), Apfloat("9.43")])

    def test_is_prime(self):
        self.assertTrue(is_prime(Apfloat("7")))

    def test_floor(self):
        self.assertEquals(floor(Apfloat("5.73")), Apfloat("5"))
        self.assertEquals(floor(Apfloat("5.22")), Apfloat("5"))

    def test_factorial(self):
        self.assertEquals(factorial(Apfloat("5")), Apfloat("120"))

    def test_sqrt(self):
        self.assertEquals(sqrt(Apfloat("225")), Apfloat("15"))

    def test_cbrt(self):
        self.assertTrue(cbrt(Apfloat("3375")) <= Apfloat("15.0"))

    def test_lcm(self):
        a: Apfloat = Apfloat("8")
        b: Apfloat = Apfloat("6")
        c: Apfloat = lcm(a, b)
        self.assertEquals(c, Apfloat("24"))

    def test_gcd(self):
        a: Apfloat = Apfloat("8")
        b: Apfloat = Apfloat("6")
        c: Apfloat = gcd(a, b)
        self.assertEquals(c, Apfloat("2"))


if __name__ == '__main__':
    unittest.main()
