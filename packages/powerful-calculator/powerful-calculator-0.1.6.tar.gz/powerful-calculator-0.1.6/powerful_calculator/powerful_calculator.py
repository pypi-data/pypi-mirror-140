'Calculator package'

import numpy as np 
import warnings
warnings.filterwarnings('ignore')

class Calculator():
    """
    This class is used for basic arithmetic opperation, like:
    addition, subtraction, dividion, multiplication and root (n).
    This class stores in memory given number on which operations can be performed.

    >>> from powerful_calculator.powerful_calculator import Calculator
    >>> calc = Calculator()
    >>> calc.add(0.1)
    0.1
    >>> calc.add(0.2)
    0.3
    >>> calc.subtract(10.3)
    -10.0
    >>> calc.divide(3)
    -3.333333333333
    >>> calc.multiply(3)
    -10.0
    >>> calc.root(1/3)
    -1000.0
    >>> calc.reset()
    0.0
    """

    def __init__(self, start_state:float= 0.0) -> None:
        self.state = float(start_state)
        
    def reset(self) -> float:
        """Resets number in memory to 0"""
        self.state = float(0)
        return self.state

    def add(self, num: float) -> float:
        """Increase number in memory"""
        self.state = round(np.add(self.state,num),12)
        return self.state

    def subtract(self, num: float) -> float:
        """Decrease number in memory"""
        self.state = round(np.subtract(self.state,num),12)
        return self.state

    def multiply(self, num: float) -> float:
        """Multiply number in memory"""

        self.state = round(np.multiply(self.state,num),10)
        return self.state

    def divide(self, num: float) -> float:
        """Divides number in memory"""
        if num == 0:
            raise Exception("Can't divide by 0")
        self.state = round(np.true_divide(self.state,num),12)
        return self.state

    def root(self, num: float) -> float:
        """Calculates (n) root of a number in memory"""
        if num == 0:
            raise Exception("Can't 0 degree root")
        self.state = round(np.power(self.state, np.divide(1.0,num)), 12)
        return self.state

    @property
    def get_state(self):
        return self.state

if __name__ == '__main__':
    import doctest
    print(doctest.testmod())