import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jose import jwt,JWTError
from pwdlib import PasswordHash

load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(username: str, role: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


bearer_scheme = HTTPBearer()


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    try:
        return jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Geçersiz veya süresi dolmuş token"
        )
def require_role(required_role: str):
    def role_checker(
        token_data: dict = Depends(get_current_token)
    ):
        if token_data.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail="Bu işlem için yetkiniz yok"
            )

        return token_data

    return role_checker