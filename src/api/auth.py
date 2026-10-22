import http, logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from infrastructure.persistence.neo4j.user_repositories import Neo4jUserRepository
from infrastructure.persistence.neo4j.client import Neo4jClient

from domain.user.exceptions import UserNotFoundError, PasswordMismatchError
from domain.auth.auth import UserAccessToken
router = APIRouter(prefix="/auth", tags=["auth"])

class LoginUserRequest(BaseModel):
    username: str
    password: str

class LoginUserResponse(BaseModel):
    status: bool
    code: int
    message: str
    token: str | None = None

    @classmethod
    def from_user(cls, token: str) -> "LoginUserResponse":
        return cls(
            status=True,
            code=http.HTTPStatus.OK,
            message="User logged-in successfully",
            token=token,
        )

@lru_cache
def get_user_repository() -> Neo4jUserRepository:
    return Neo4jUserRepository(Neo4jClient())
# def register_user(
#         payload: UserRegisterRequest,
#         repo: Neo4jUserRepository = Depends(get_user_repository),
# ) -> UserRegisterResponse:
#     return repo.register(payload)

@router.post("/login", response_model=LoginUserResponse, status_code=status.HTTP_200_OK)
def login(
        payload: LoginUserRequest,
        repo: Neo4jUserRepository = Depends(get_user_repository)
) -> LoginUserResponse:
    logging.info("inside logging")
    try:
        user_id = repo.valid_credentials(username=payload.username, password=payload.password)

        token = UserAccessToken.create_access_token(user_id)
        return LoginUserResponse.from_user(token)

    except PasswordMismatchError:
        return LoginUserResponse(status=False, code=http.HTTPStatus.UNAUTHORIZED,
                                 message="Incorrect username or password")

    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc





