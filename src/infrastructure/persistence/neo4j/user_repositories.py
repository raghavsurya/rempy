import logging
from domain.user.exceptions import UserAlreadyExistsError, PasswordMismatchError
from domain.user.repositories import UserRepository
from domain.user.user import User
from infrastructure.persistence.neo4j.client import Neo4jClient
from neo4j.exceptions import ConstraintError
from argon2 import PasswordHasher, exceptions

from domain.user.exceptions import UserNotFoundError

_ADD_USER_QUERY = """
MERGE (u:User {username: $username})
ON CREATE SET
    u.id = $id,
    u.password = $password,
    u.email = $email,
    u.gender = $gender,
    u.num_of_reminders = $num_of_reminders
RETURN u, id(u) AS user_id, u.id = $id AS created
"""

_DELETE_USER_QUERY = """
MATCH(u:User {username: $username})
DELETE u
"""

_LIST_USERS_QUERY = "MATCH (u:User) RETURN u, id(u) AS user_id ORDER BY u.username"

_CONSTRAINT_EMAIL_QUERY = """
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE
"""

_CONSTRAINT_USERNAME_QUERY = """
CREATE CONSTRAINT user_username_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.username IS UNIQUE
"""
_UPDATE_PASSWORD_HASH_QUERY = """
MATCH (u:User {username: $username})
SET u.password = $password,
"""


class Neo4jUserRepository(UserRepository):
    """Neo4j-backed implementation of the UserRepository port."""

    def __init__(self, client: Neo4jClient):
        self._client = client

    @staticmethod
    def create_constraints(tx) -> None:
        tx.run(_CONSTRAINT_USERNAME_QUERY)
        tx.run(_CONSTRAINT_EMAIL_QUERY)

    def ensure_schema(self) -> None:
        """Create the uniqueness constraint backing add()'s duplicate check."""
        with self._client.session() as session:
            #session.run()
            session.execute_write(self.create_constraints)


    def add(self, user: User) -> User:
        data = user.to_dict()
        try:
            with self._client.session() as session:
                record = session.run(_ADD_USER_QUERY, **data).single()
        except ConstraintError:
            logging.error("constraint failed")
            raise UserAlreadyExistsError(user.username)

        return User.from_dict(dict(record["u"]), user_id=record["user_id"])

    def list_users(self) -> list[User]:
        with self._client.session() as session:
            result = session.run(_LIST_USERS_QUERY)
            return [User.from_dict(dict(record["u"]), user_id=record["user_id"]) for record in result]

    def delete_user(self, username: str):
        with self._client.session() as session:
            session.run(_DELETE_USER_QUERY, username=username)

    def update_password_hash(self, username: str, password_hash: str):
        with self._client.session() as session:
            session.run(_UPDATE_PASSWORD_HASH_QUERY, username=username, password_hash=password_hash)

    def valid_credentials(self, username: str, password: str) -> int:
        with self._client.session() as session:
            result = session.run("""
                    MATCH (u:User {username: $username})
                    RETURN u, id(u) AS user_id;
                    """, username=username).single()
        if result is None:
            raise UserNotFoundError(username)

        record = User.from_dict(dict(result["u"]), user_id=result["user_id"])
        ph = PasswordHasher()
        try:
            ph.verify(record.password, password)
        except exceptions.VerificationError:
            raise PasswordMismatchError(username)


        if ph.check_needs_rehash(record.password):
            logging.info("password hash changed")
            hashed_pwd = User.hash_password(record.password)
            self.update_password_hash(username, hashed_pwd)

        return record.user_id


    #TODO: rehash the password again by calling
    # if ph.check_needs_rehash(hash):
    #         db.set_password_hash_for_user(user, ph.hash(password))

