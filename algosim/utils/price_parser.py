
from multipledispatch import dispatch
import numpy as np

int_t = (int, np.int64)


class PriceParser(object):
    """
    PriceParser is designed to abstract away the underlying number used as a price
    within this project. Due to efficiency and floating point precision limitations,
    Dali uses an integer to represent all prices. This means that $0.10 is,
    internally, 10,000,000. Because such large numbers are rather unwieldy
    for humans, the PriceParser will take "normal" 2dp numbers as input, and show
    "normal" 2dp numbers as output when requested to `display()`

    For consistency's sake, PriceParser should be used for ALL prices that enter
    the dali system. Numbers should also always be parsed correctly to view.

    """

    # 10,000,000
    PRICE_MULTIPLIER = 10000000

    """Parse Methods. Multiplies a float out into an int if needed."""

    @staticmethod
    @dispatch(int_t)
    def parse(x):  # flake8: noqa
        return x

    @staticmethod
    @dispatch(str)
    def parse(x):  # flake8: noqa
        return int(float(x) * PriceParser.PRICE_MULTIPLIER)

    @staticmethod
    @dispatch(float)
    def parse(x):  # flake8: noqa
        return int(x * PriceParser.PRICE_MULTIPLIER)

    """Display Methods. Multiplies a float out into an int if needed."""

    @staticmethod
    @dispatch(int_t)
    def display(x):  # flake8: noqa
        return round(x / PriceParser.PRICE_MULTIPLIER, 2)

    @staticmethod
    @dispatch(float)
    def display(x):  # flake8: noqa
        return round(x, 2)

    @staticmethod
    @dispatch(int_t, int)
    def display(x, dp):  # flake8: noqa
        return round(x / PriceParser.PRICE_MULTIPLIER, dp)

    @staticmethod
    @dispatch(float, int)
    def display(x, dp):  # flake8: noqa
        return round(x, dp)
