from neo4j import Driver, GraphDatabase
from pydantic_settings import BaseSettings, SettingsConfigDict


class Neo4jSettings(BaseSettings):
    """Connection settings, overridable via NEO4J_* environment variables."""

    model_config = SettingsConfigDict(env_prefix="NEO4J_")

    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"


class Neo4jClient:
    """Thin wrapper around the official Neo4j driver managing its lifecycle."""

    def __init__(self, settings: Neo4jSettings | None = None):
        self._settings = settings or Neo4jSettings()
        self._driver: Driver = GraphDatabase.driver(
            self._settings.uri,
            auth=(self._settings.user, self._settings.password),
        )
        with self._driver.session(database="reminders") as session:
            _result = session.run("MATCH (n) RETURN n LIMIT 1")

    def verify_connectivity(self) -> None:
        self._driver.verify_connectivity()

    def session(self):
        return self._driver.session()

    def close(self) -> None:
        self._driver.close()

    def __enter__(self) -> "Neo4jClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
