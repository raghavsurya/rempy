from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from domain.user.exceptions import InvalidEmailError, UserAlreadyExistsError
from domain.user.user import User
from domain.user.value_objects import Gender
from infrastructure.persistence.neo4j.client import Neo4jClient
from infrastructure.persistence.neo4j.user_repositories import Neo4jUserRepository

from domain.user.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: str
    gender: Gender = Gender.MALE
    num_of_reminders: int = 0

class UserDeleteRequest(BaseModel):
    username: str

class UserCheckRequest(BaseModel):
    username: str
    password: str

class UserDeleteResponse(BaseModel):
    message: str
    code: int

    @classmethod
    def from_user(cls, message: str, code: int) -> "UserDeleteResponse":
        return cls(message=message, code=code)

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    gender: str
    num_of_reminders: int

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            username=user.username,
            email=str(user.email),
            gender=user.gender.name,
            num_of_reminders=user.num_of_reminders,
        )


@lru_cache
def get_user_repository() -> Neo4jUserRepository:
    """Lazily create a single Neo4j-backed repository for the app's lifetime."""
    return Neo4jUserRepository(Neo4jClient())


@router.post("/v1", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_user(
    payload: UserCreateRequest,
    repo: Neo4jUserRepository = Depends(get_user_repository),
) -> UserResponse:
    try:
        user = User(
            username=payload.username,
            password=payload.password,
            email=payload.email,
            gender=payload.gender,
            num_of_reminders=payload.num_of_reminders,
        )
        created = repo.add(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidEmailError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return UserResponse.from_user(created)


@router.get("/v1", response_model=list[UserResponse])
def list_users(
    repo: Neo4jUserRepository = Depends(get_user_repository),
) -> list[UserResponse]:
    return [UserResponse.from_user(user) for user in repo.list_users()]

@router.post("/v1/delete", response_model=None, status_code=status.HTTP_200_OK)
def delete_user(
        payload: UserDeleteRequest,
        repo: Neo4jUserRepository = Depends(get_user_repository),

) -> status.HTTP_200_OK:
    try:
        repo.delete_user(username=payload.username)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return UserDeleteResponse.from_user(message="user deleted successfully", code=int(status.HTTP_200_OK))

@router.post("/v1/check", response_model=None, status_code=status.HTTP_200_OK)
def check_user(
        payload: UserCheckRequest,
        repo: Neo4jUserRepository = Depends(get_user_repository),
) -> tuple[bool, str | None]:
    valid = repo.valid_credentials(username=payload.username, password=payload.password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return True, None