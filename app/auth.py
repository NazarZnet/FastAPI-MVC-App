import json
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Security
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, redis_client
from app.models import User
from config import (
    SECRET_KEY,
    REFRESH_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    BLACKLISTED_TOKENS_EXPIRY,
    USER_CACHE_EXPIRE,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


from config import BLACKLISTED_TOKENS_EXPIRY


def blacklist_token(token: str):
    """Blacklists a JWT token by storing it in Redis for its remaining validity period."""
    payload = decode_token(token, SECRET_KEY)
    if not payload:
        return  # Token is invalid, ignore it

    exp_time = payload.get("exp")
    if exp_time:
        ttl = exp_time - int(datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            redis_client.setex(
                f"blacklist:{token}", min(ttl, BLACKLISTED_TOKENS_EXPIRY), "blacklisted"
            )


def is_token_blacklisted(token: str) -> bool:
    """Checks if a token is blacklisted."""
    return redis_client.exists(f"blacklist:{token}") > 0


def hash_password(password: str) -> str:
    """Hashes a password securely using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if a plaintext password matches its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generates a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generates a JWT refresh token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    data.update({"exp": expire})
    return jwt.encode(data, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, secret_key: str) -> dict | None:
    """Decodes a JWT token and verifies expiration."""
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    token: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> User:
    """Extracts the authenticated user from the JWT token and caches user data in Redis."""
    if is_token_blacklisted(token.credentials):
        raise HTTPException(status_code=401, detail="Token is blacklisted")

    payload = decode_token(token.credentials, SECRET_KEY)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_email = payload["sub"]

    try:
        # Check if user data is cached in Redis
        cached_user = redis_client.get(f"user:{user_email}")
        if cached_user:
            user_data = json.loads(cached_user)
            return User(
                id=user_data["id"],
                email=user_data["email"],
                hashed_password=user_data["hashed_password"],
            )

    except Exception:
        pass  # Fallback to database if Redis fails

    # Fetch user from database
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Serialize user data for caching (excluding `_sa_instance_state`)
    user_data = {
        "id": user.id,
        "email": user.email,
        "hashed_password": user.hashed_password,
    }
    redis_client.setex(f"user:{user_email}", USER_CACHE_EXPIRE, json.dumps(user_data))

    return user
