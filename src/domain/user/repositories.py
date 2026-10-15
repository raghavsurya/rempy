from abc import ABC, abstractmethod

from domain.user.user import User


class UserRepository(ABC):
    """Port describing how the domain persists and retrieves users.

    Infrastructure adapters (e.g. Neo4j) implement this interface so the
    domain layer stays free of persistence details.
    """

    @abstractmethod
    def add(self, user: User) -> User:
        """Persist a new user. Raises UserAlreadyExistsError on conflict."""

    @abstractmethod
    def list_users(self) -> list[User]:
        """Return every persisted user."""
