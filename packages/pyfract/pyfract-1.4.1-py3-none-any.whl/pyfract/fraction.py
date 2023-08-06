from math import floor
from pyfract.src.utils import greatest_common_divisor


class Fraction:
    """
    Fraction object full implementation
    """
    numerator: int
    denominator: int

    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator

    def __repr__(self):
        return f'[{self.numerator}/{self.denominator}]'

    def fancy_repr(self):
        """
        Another implementation of __repr__ but the fraction is represented in a realistic way
        """
        n_len = len(str(self.numerator))
        d_len = len(str(self.denominator))

        line_len = max(n_len, d_len) + 2

        # Counting spaces to print the fraction centered
        n_space = ' ' * floor((line_len - n_len) / 2)
        d_space = ' ' * floor((line_len - d_len) / 2)

        return f'{n_space}{self.numerator}{n_space}\n{"‒" * line_len}\n{d_space}{self.denominator}{d_space}'

    def to_float(self) -> float:
        """
        Returns the fraction value in a float
        """
        return self.numerator / self.denominator

    def simplify(self):
        """
        Converts the fraction to the simplest version.

        e.g.
        [2/4] -> [1/2]
        [4/10] -> [2/5]
        """
        gcd = greatest_common_divisor(self.numerator, self.denominator)
        p = self.numerator // gcd
        q = self.denominator // gcd

        # If denominator of the fraction is negative,
        # change negativity to the numerator to keep the convention
        # e.g. [1/-2] -> [-1/2]
        if q < 0:
            q = -q
            p = -p

        return Fraction(p, q)

    def __add__(self, other):
        other = Fraction.__normalize_type(other)
        p = (self.numerator * other.denominator) + (other.numerator * self.denominator)
        q = self.denominator * other.denominator
        return Fraction(p, q).simplify()

    def __sub__(self, other):
        other = Fraction.__normalize_type(other)
        p = (self.numerator * other.denominator) - (other.numerator * self.denominator)
        q = self.denominator * other.denominator
        return Fraction(p, q).simplify()

    def __mul__(self, other):
        other = Fraction.__normalize_type(other)
        p = self.numerator * other.numerator
        q = self.denominator * other.denominator
        return Fraction(p, q).simplify()

    def __truediv__(self, other):
        other = Fraction.__normalize_type(other)
        p = self.numerator * other.denominator
        q = self.denominator * other.numerator
        return Fraction(p, q).simplify()

    def __lt__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() < other

    def __le__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() <= other.to_float()

    def __gt__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() > other.to_float()

    def __ge__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() >= other.to_float()

    def __eq__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() == other.to_float()

    def __ne__(self, other):
        other = Fraction.__normalize_type(other)
        return self.to_float() != other.to_float()

    @staticmethod
    def __normalize_type(_object):
        """
        Check type of gotten object and converts it to the Fraction
        It is used for addition, subtraction, multiplication and division implementation of Fraction
        """
        if isinstance(_object, int):
            return Fraction(_object, 1)
        elif isinstance(_object, float):
            return Fraction.from_float_accurately(_object)
        else:
            return _object

    @staticmethod
    def from_float(number: float):
        """
        Converts a float number to the Fraction and returns it
        """

        # Convert number to float just in case of int given
        number = float(number)

        """
        Float is in decimal number system so it takes the `number` 
        and generates its representation in fraction x/10^y
         
        e.g:
        0.32 -> [32/100]
        1.323 -> [1323/1000]
        """
        digits_after_period = len(str(number).split('.')[1])
        p = round((number * 10 ** digits_after_period))
        q = 10 ** digits_after_period

        # Here the generated fraction is being simplified
        return Fraction(p, q).simplify()

    @staticmethod
    def from_float_accurately(number: float, accuracy: int = 8):
        """
        Converts a float number to the Fraction and returns it
        but more accurately than `from_float()`

        Attributes
        --------
        number : float
            The number to convert
        accuracy : int
            How many digits after the period the Fraction has to be accurate
        """
        if number == 0:
            return Fraction(0, 1)

        is_negative = number < 0

        # If `number` is negative, numerator of the fraction has to be negative
        # since negative divided by positive is negative
        p = 1 if not is_negative else -1
        q = 1

        # Guessing the fraction numerator and denominator by balancing between both values
        while True:
            num = p / q

            if round(num, accuracy) == round(number, accuracy):
                return Fraction(p, q)
            else:
                if not is_negative:
                    if num < number:
                        p += 1
                    elif num > number:
                        q += 1
                else:
                    if num > number:
                        p -= 1
                    elif num < number:
                        q += 1
