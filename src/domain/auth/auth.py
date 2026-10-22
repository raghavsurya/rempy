import os
import jwt
from datetime import datetime, timedelta, timezone


SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
algorithm = os.environ.get("ALGORITHM")


class UserAccessToken:
    @staticmethod
    def create_access_token(user_id: int | str) -> str:
        """
        Creates a JWT token on successful login
        :param user_id:
        :return: jwt token
        """
        now = datetime.now(timezone.utc)
        payload = {
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "sub": str(user_id)

        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=algorithm,
        )
