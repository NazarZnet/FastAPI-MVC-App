from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models import User
from .database import get_db
from .schemas import PostResponse, UserCreate, PostCreate, Token
from .services import (
    create_user,
    authenticate_user,
    add_post,
    delete_post,
    get_user_posts,
)
from .auth import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    security,
)
from config import MAX_POST_SIZE_BYTES, REFRESH_SECRET_KEY

router = APIRouter()


@router.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user and returns both access and refresh tokens."""
    user = create_user(db, user)
    return {
        "access_token": create_access_token({"sub": user.email}),
        "refresh_token": create_refresh_token({"sub": user.email}),
    }


@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """Logs in the user and returns tokens if authentication is successful."""
    tokens = authenticate_user(db, user.email, user.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return tokens


@router.post("/logout")
def logout(token: HTTPAuthorizationCredentials = Depends(security)):
    """Logs out a user by blacklisting their access token."""
    blacklist_token(token.credentials)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str = Header(None)):
    """
    Generates a new access token using the provided refresh token.
    Ensures token validity before issuing a new access token.
    """
    payload = decode_token(refresh_token, secret_key=REFRESH_SECRET_KEY)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access_token}


@router.post("/posts", response_model=PostResponse)
def add_post_endpoint(
    post: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Creates a new post for the authenticated user.

    - Requires a valid JWT token.
    - Limits post text size to 1MB.
    - Ensures the user exists before adding a post.
    """

    # Validate post size (max 1MB)
    if len(post.text.encode("utf-8")) > MAX_POST_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Post size exceeds 1MB limit")

    return add_post(db, post, user_id=user.id)


@router.get("/posts", response_model=list[PostResponse])
def get_posts_endpoint(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Returns all posts for the authenticated user with Redis caching.

    - Uses Redis to cache posts for 5 minutes.
    - Reduces database queries for frequent requests.
    """
    return get_user_posts(db, user.id)


@router.delete("/posts/{post_id}")
def delete_post_endpoint(
    post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Deletes a post if the authenticated user owns it.

    - Requires a valid JWT token.
    - Ensures the post exists and belongs to the user before deletion.
    - Returns an error if the post does not exist or belongs to another user.
    """
    result = delete_post(db, user.id, post_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
