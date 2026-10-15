import http
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from domain.user.user import User
from torch.fx.experimental.symbolic_shapes import lru_cache

from src.domain.user.value_objects import Gender
from infrastucture.persistence.neo4j.user_repositories import Neo4jUserRepository
from infrastucture.persistence.neo4j.client import Neo4jClient


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    dob: datetime
    gender: Gender = Gender.FEMALE

class UserRegisterResponse(BaseModel):
    status: bool
    code: int
    message: str

    @classmethod
    def from_user(cls, user: User) -> "UserRegisterResponse":
        return cls(
            status=True,
            code=http.HTTPStatus.CREATED,
            message="User registered successfully",
        )

@lru_cache
def get_user_repository(user: User) -> Neo4jUserRepository:
    return Neo4jUserRepository(Neo4jClient())
def register_user(
        payload: UserRegisterRequest,
        repo: Neo4jUserRepository = Depends(get_user_repository),
) -> UserRegisterResponse:
    return repo.register(payload)




