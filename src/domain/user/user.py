from dataclasses import dataclass, field
from uuid import UUID, uuid4
from argon2 import PasswordHasher
import logging

from domain.user.value_objects import Email, Gender


@dataclass
class User:
    """Domain entity representing a user."""

    username: str
    password: str
    email: Email
    gender: Gender = Gender.MALE
    num_of_reminders: int = 0

    id: UUID = field(default_factory=uuid4)
    user_id: int | None = None

    def __post_init__(self):
        if not isinstance(self.email, Email):
            self.email = Email(self.email)
        if not isinstance(self.gender, Gender):
            self.gender = Gender(self.gender)

    def to_dict(self) -> dict:
        """Flatten the entity into primitives suitable for persistence."""
        password = self.hash_password(self.password)
        return {
            "id": str(self.id),
            "username": self.username,
            "password": password,
            "email": str(self.email),
            "gender": self.gender.value,
            "num_of_reminders": self.num_of_reminders,
        }

    @classmethod
    def from_dict(cls, data: dict, user_id: int | None = None) -> "User":
        """Rehydrate a User from a persisted record (e.g. a Neo4j node).

        `user_id` is Neo4j's internal node id, which isn't a node property so
        it's passed in separately (e.g. from `id(u)` in the Cypher query).
        """
        user = cls(
            username=data["username"],
            password=data.get("password", ""),
            email=data["email"],
            gender=data.get("gender", Gender.MALE.value),
            num_of_reminders=data.get("num_of_reminders", 0),
            user_id=user_id,
        )
        user.id = UUID(str(data["id"]))
        return user

    @staticmethod
    def hash_password(password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)
