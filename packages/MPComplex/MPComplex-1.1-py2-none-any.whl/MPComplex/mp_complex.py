"""
This file contains code for the library "MPComplex".
Author: DigitalCreativeApkDev
"""


# Importing necessary libraries
import copy

from mpmath import *
mp.pretty = True


# Creating static function to check whether an object is a number or not


def is_number(obj: object) -> bool:
    try:
        mpf(str(obj))
        return True
    except ValueError:
        return False


class MPComplex:
    """
    This class contains attributes of a complex number in mpmath.
    """

    def __init__(self, real_part=mpf("0"), imaginary_part=mpf("0")):
        # type: (mpf, mpf) -> None
        self.real_part: mpf = real_part
        self.imaginary_part: mpf = imaginary_part

    def __add__(self, other):
        # type: (object) -> MPComplex
        if isinstance(other, MPComplex):
            return MPComplex(self.real_part + other.real_part, self.imaginary_part + other.imaginary_part)
        elif is_number(other):
            return MPComplex(self.real_part + mpf(other), self.imaginary_part)
        else:
            raise TypeError("Unsupported operand type '+' for type 'MPComplex' with '" +
                            str(type(other)) + "'!")

    def __sub__(self, other):
        # type: (object) -> MPComplex
        if isinstance(other, MPComplex):
            return MPComplex(self.real_part - other.real_part, self.imaginary_part - other.imaginary_part)
        elif is_number(other):
            return MPComplex(self.real_part - mpf(other), self.imaginary_part)
        else:
            raise TypeError("Unsupported operand type '-' for type 'MPComplex' with '" +
                            str(type(other)) + "'!")

    def conjugate(self):
        # type: () -> MPComplex
        return MPComplex(self.real_part, self.imaginary_part * mpf("-1"))

    def __mul__(self, other):
        # type: (object) -> MPComplex
        if isinstance(other, MPComplex):
            first_real_part: mpf = self.real_part * other.real_part
            first_imag_part: mpf = self.real_part * other.imaginary_part
            second_imag_part: mpf = self.imaginary_part * other.real_part
            second_real_part: mpf = self.imaginary_part * other.imaginary_part * mpf("-1")
            return MPComplex(first_real_part + second_real_part, first_imag_part + second_imag_part)
        elif is_number(other):
            return MPComplex(self.real_part * mpf(other), self.imaginary_part * mpf(other))
        else:
            raise TypeError("Unsupported operand type '*' for type 'MPComplex' with '" +
                            str(type(other)) + "'!")

    def clone(self):
        # type: () -> MPComplex
        return copy.deepcopy(self)

    def __pow__(self, other):
        # type: (int) -> MPComplex
        curr: MPComplex = self.clone()
        now: MPComplex = curr.clone()
        for i in range(other - 1):
            now *= curr

        return now

    def __truediv__(self, other):
        # type: (object) -> MPComplex
        if isinstance(other, MPComplex):
            first: MPComplex = self.__mul__(other.conjugate())
            second: MPComplex = other.__mul__(other.conjugate())
            return MPComplex(first.real_part / second.real_part, first.imaginary_part / second.real_part)
        elif is_number(other):
            return MPComplex(self.real_part / mpf(other), self.imaginary_part / mpf(other))
        else:
            raise TypeError("Unsupported operand type '/' for type 'MPComplex' with '" +
                            str(type(other)) + "'!")

    def __floordiv__(self, other):
        # type: (object) -> MPComplex
        if isinstance(other, MPComplex):
            first: MPComplex = self.__mul__(other.conjugate())
            second: MPComplex = other.__mul__(other.conjugate())
            return MPComplex(floor(first.real_part / second.real_part), mpf("0"))
        elif is_number(other):
            return MPComplex(floor(self.real_part / mpf(other)), mpf("0"))
        else:
            raise TypeError("Unsupported operand type '//' for type 'MPComplex' with '" +
                            str(type(other)) + "'!")

    def __gt__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            if self.real_part > other.real_part:
                return True
            elif self.real_part == other.real_part:
                return self.imaginary_part > other.imaginary_part
            else:
                return False
        elif is_number(other):
            if self.real_part > mpf(other):
                return True
            elif self.real_part == mpf(other):
                return self.imaginary_part > 0
            else:
                return False
        else:
            raise TypeError("'>' not supported between instances of 'MPComplex' and '" + str(type(other)) + "'!")

    def __lt__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            if self.real_part < other.real_part:
                return True
            elif self.real_part == other.real_part:
                return self.imaginary_part < other.imaginary_part
            else:
                return False
        elif is_number(other):
            if self.real_part < mpf(other):
                return True
            elif self.real_part == mpf(other):
                return self.imaginary_part < 0
            else:
                return False
        else:
            raise TypeError("'<' not supported between instances of 'MPComplex' and '" + str(type(other)) + "'!")

    def __le__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            if self.real_part <= other.real_part:
                return True
            elif self.real_part == other.real_part:
                return self.imaginary_part <= other.imaginary_part
            else:
                return False
        elif is_number(other):
            if self.real_part <= mpf(other):
                return True
            elif self.real_part == mpf(other):
                return self.imaginary_part <= 0
            else:
                return False
        else:
            raise TypeError("'<=' not supported between instances of 'MPComplex' and '" + str(type(other)) + "'!")

    def __ge__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            if self.real_part >= other.real_part:
                return True
            elif self.real_part == other.real_part:
                return self.imaginary_part >= other.imaginary_part
            else:
                return False
        elif is_number(other):
            if self.real_part >= mpf(other):
                return True
            elif self.real_part == mpf(other):
                return self.imaginary_part >= 0
            else:
                return False
        else:
            raise TypeError("'>=' not supported between instances of 'MPComplex' and '" + str(type(other)) + "'!")

    def __eq__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            return self.real_part == other.real_part and self.imaginary_part == other.imaginary_part
        elif is_number(other):
            return self.real_part == mpf(other) and self.imaginary_part == mpf("0")
        else:
            return False

    def __ne__(self, other):
        # type: (object) -> bool
        if isinstance(other, MPComplex):
            return not (self.real_part == other.real_part and self.imaginary_part == other.imaginary_part)
        elif is_number(other):
            return not (self.real_part == mpf(other) and self.imaginary_part == mpf("0"))
        else:
            return True

    def __neg__(self):
        # type: () -> MPComplex
        return MPComplex(self.real_part * mpf("-1"), self.imaginary_part * mpf("-1"))

    def __str__(self):
        # type: () -> str
        if self.imaginary_part < 0:
            return str(self.real_part) + " - " + str(abs(self.imaginary_part)) + "j"
        elif self.imaginary_part == 0:
            return str(self.real_part)
        else:
            return str(self.real_part) + " + " + str(abs(self.imaginary_part)) + "j"

