from dataclasses import dataclass
from enum import Enum

from domain.user.exceptions import InvalidEmailError


class Gender(Enum):
    MALE = 1
    FEMALE = 2
    TRANS = 3


@dataclass(frozen=True)
class Email:
    """Value object guaranteeing a syntactically valid email address."""

    value: str

    def __post_init__(self):
        if "@" not in self.value or "." not in self.value.rsplit("@", 1)[-1]:
            raise InvalidEmailError(self.value)

    def __str__(self) -> str:
        return self.value
