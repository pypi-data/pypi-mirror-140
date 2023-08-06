"""
Definition of custom exceptions

Created on: 23/02/2022
Author: Alexandre Bohyn
"""


class DesignIndexError(Exception):
    """Raised when an index does not correspond to a design in the database"""

    def __init__(self, index: str = "Given index"):
        self.index = index

    def __str__(self):
        return f"{self.index} is not a valid index"


class RunSizeError(Exception):
    """Raised when the run size is not a power of two"""

    def __init__(self, run_size: int):
        self.run_size = run_size

    def __str__(self):
        return f"Given run size of {self.run_size} is not a power of two"


if __name__ == "__main__":
    pass
