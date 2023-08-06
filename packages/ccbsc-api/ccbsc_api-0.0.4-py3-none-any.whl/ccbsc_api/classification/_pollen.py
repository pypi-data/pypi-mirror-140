from enum import Enum


class Pollen(str, Enum):
    ALTERNARIA = "Alternaria"

    def __str__(self) -> str:
        return str.__str__(self)