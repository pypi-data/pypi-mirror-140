"""
This file contains code for the library "Apfloat".
Author: DigitalCreativeApkDev
"""


# Importing necessary libraries
from MPComplex.mp_complex import MPComplex
from mpmath import *
mp.pretty = True


# Creating static function to check whether an object is a number or not


def is_number(obj: object) -> bool:
    try:
        mpf(str(obj))
        return True
    except ValueError:
        return False


class Apfloat(MPComplex):
    """
    This class contains attributes of an Apfloat
    """

    def __init__(self, value):
        # type: (mpf or str or float or int) -> None
        MPComplex.__init__(self, real_part=mpf(value))

    def conjugate(self):
        # type: () -> Apfloat
        return self

    def __pow__(self, other):
        # type: (mpf or str or float or int or MPComplex) -> Apfloat
        if isinstance(other, MPComplex):
            return Apfloat(self.real_part ** mpf(other.real_part))
        return Apfloat(self.real_part ** mpf(other))

    def __mod__(self, other):
        # type: (mpf or str or float or int or MPComplex) -> Apfloat
        if isinstance(other, MPComplex):
            return Apfloat(self.real_part % mpf(other.real_part))
        return Apfloat(self.real_part % mpf(other))

    def __int__(self):
        # type: () -> int
        return int(self.real_part)

    def squared(self):
        # type: () -> Apfloat
        return self.__pow__(2)

    def cubed(self):
        # type: () -> Apfloat
        return self.__pow__(3)

    def __float__(self):
        # type: () -> float
        if self.real_part < mpf("2.2250738585072014e-308"):
            raise Exception("Underflow! The BigNumber object is too small to be converted to a float!")
        elif self.real_part > mpf("1.7976931348623157e+308"):
            raise Exception("Overflow! The BigNumber object is too large to be converted to a float!")
        else:
            return float(self.real_part)

    def __pos__(self):
        # type: () -> Apfloat
        return Apfloat(self.real_part)

    def __abs__(self):
        # type: () -> Apfloat
        if self.real_part < 0:
            return self.__neg__()
        return self.__pos__()

    def __floor__(self):
        # type: () -> Apfloat
        return Apfloat(floor(self.real_part))

    def __ceil__(self):
        # type: () -> Apfloat
        return Apfloat(ceil(self.real_part))

    def __and__(self, other):
        # type: (MPComplex or str or float or int or mpf) -> Apfloat
        if self.real_part == 0:
            return self
        else:
            if isinstance(other, MPComplex):
                return other
            else:
                return Apfloat(mpf(other))

    def __or__(self, other):
        # type: (MPComplex or str or float or int or mpf) -> Apfloat
        if self.real_part != 0:
            return self
        else:
            if isinstance(other, MPComplex):
                return other
            else:
                return Apfloat(mpf(other))


# Creating additional methods for Apfloat class.


def to_mpf(apfloat: Apfloat) -> mpf:
    return mpf(apfloat.real_part)


def floor(apfloat: Apfloat) -> Apfloat:
    return apfloat // Apfloat("1")


def sqrt(apfloat: Apfloat) -> Apfloat:
    return apfloat.__pow__(mpf("0.5"))


def cbrt(apfloat: Apfloat) -> Apfloat:
    one_third: mpf = mpf("1") / mpf("3")
    return apfloat.__pow__(one_third)


def sin(apfloat: Apfloat) -> Apfloat:
    return Apfloat(sin(apfloat.real_part))


def cos(apfloat: Apfloat) -> Apfloat:
    return Apfloat(cos(apfloat.real_part))


def tan(apfloat: Apfloat) -> Apfloat:
    return Apfloat(tan(apfloat.real_part))


def cosec(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(sin(apfloat.real_part))


def sec(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(cos(apfloat.real_part))


def cot(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(tan(apfloat.real_part))


def sinh(apfloat: Apfloat) -> Apfloat:
    return Apfloat(sinh(apfloat.real_part))


def cosh(apfloat: Apfloat) -> Apfloat:
    return Apfloat(cosh(apfloat.real_part))


def tanh(apfloat: Apfloat) -> Apfloat:
    return Apfloat(tanh(apfloat.real_part))


def cosech(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(sinh(apfloat.real_part))


def sech(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(cosh(apfloat.real_part))


def coth(apfloat: Apfloat) -> Apfloat:
    return Apfloat("1") / Apfloat(tanh(apfloat.real_part))


def factorial(apfloat: Apfloat) -> Apfloat:
    return gamma(apfloat.real_part + mpf("1"))


def ln(apfloat: Apfloat) -> Apfloat:
    return log(apfloat.real_part)


def log_e(apfloat: Apfloat) -> Apfloat:
    return ln(apfloat.real_part)


def log_10(apfloat: Apfloat) -> Apfloat:
    return log10(apfloat.real_part)


def log_base(apfloat: MPComplex, base: MPComplex or mpf or float or int) -> Apfloat:
    if isinstance(base, MPComplex):
        return log_10(apfloat.real_part) / log_10(base.real_part)
    else:
        return log_10(apfloat.real_part) / log10(mpf(base))


def is_prime(apfloat: Apfloat) -> bool:
    if apfloat.real_part % 1 == mpf("0"):
        up_range: int = int(floor(sqrt(apfloat)).real_part)
        factors: list = [i for i in range(1, up_range) if apfloat // mpf(i) == apfloat / mpf(i)] + [apfloat.real_part]
        return len(factors) == 2
    return False


# The two following functions (obtaining GCD and LCM of two numbers) are inspired by the following source.
# https://www.geeksforgeeks.org/program-to-find-lcm-of-two-numbers/


def gcd(a: Apfloat, b: Apfloat) -> Apfloat:
    if a.real_part == mpf("0"):
        return b
    return gcd(b % a, a)


def lcm(a: Apfloat, b: Apfloat) -> Apfloat:
    return (a / gcd(a, b)) * b
