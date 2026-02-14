from enum import Enum
from colorama import Fore as color


class Color(Enum):
    RED = color.LIGHTRED_EX
    YELLOW = color.LIGHTYELLOW_EX
    GREEN = color.LIGHTGREEN_EX
    CYAN = color.LIGHTCYAN_EX
    BLUE = color.LIGHTBLUE_EX
    MAGENTA = color.LIGHTMAGENTA_EX
    ULTRA_WHITE = color.LIGHTWHITE_EX
    WHITE = color.RESET
    GRAY = color.WHITE
    BLACK = color.LIGHTBLACK_EX

    def __radd__(self, other: str) -> str:
        return other + str(self.value)

    def __add__(self, other: str) -> str:
        return str(self.value) + other

    def __str__(self) -> str:
        return self.value
