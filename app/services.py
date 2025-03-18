import json
from sqlalchemy.orm import Session
from .models import User, Post
from .schemas import PostCreate, UserCreate
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from .database import redis_client
from config import POST_CACHE_EXPIRE


def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user with a hashed password.

    Args:
        db (Session): Database session.
        user (UserCreate): User registration data.

    Returns:
        User: The newly created user object.
    """
    hashed_pw = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> dict | None:
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        db (Session): Database session.
        email (str): User email.
        password (str): User password.

    Returns:
        dict: JWT access and refresh tokens if authentication succeeds.
        None: If authentication fails.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return {
        "access_token": create_access_token({"sub": user.email}),
        "refresh_token": create_refresh_token({"sub": user.email}),
    }


def add_post(db: Session, post: PostCreate, user_id: int) -> Post:
    """
    Adds a new post for an authenticated user.

    Args:
        db (Session): Database session.
        post (PostCreate): Post creation data.
        user_id (int): ID of the user creating the post.

    Returns:
        Post: The newly created post object.
    """
    db_post = Post(text=post.text, owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    # Invalidate Redis cache for user's posts
    redis_client.delete(f"user_posts:{user_id}")

    return db_post


def get_user_posts(db: Session, user_id: int) -> list[dict]:
    """
    Retrieves all posts for a given user with Redis caching.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user whose posts are retrieved.

    Returns:
        list[dict]: List of posts belonging to the user.
    """
    cache_key = f"user_posts:{user_id}"

    # Check Redis cache first
    cached_posts = redis_client.get(cache_key)
    if cached_posts:
        return json.loads(cached_posts)

    # Query the database if cache miss
    posts = db.query(Post).filter(Post.owner_id == user_id).all()

    # Serialize posts correctly
    serialized_posts = [
        {"id": post.id, "text": post.text, "owner_id": post.owner_id} for post in posts
    ]

    # Store in Redis as valid JSON
    redis_client.setex(cache_key, POST_CACHE_EXPIRE, json.dumps(serialized_posts))

    return serialized_posts


def delete_post(db: Session, user_id: int, post_id: int) -> dict:
    """
    Deletes a post if it belongs to the authenticated user.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user attempting deletion.
        post_id (int): ID of the post to be deleted.

    Returns:
        dict: Success message if deletion succeeds.
        dict: Error message if post does not exist or user lacks permission.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user_id).first()

    if not post:
        return {"error": "Post not found or you don't have permission to delete it"}

    db.delete(post)
    db.commit()

    # Invalidate Redis cache for user's posts
    redis_client.delete(f"user_posts:{user_id}")

    return {"message": "Post deleted successfully"}
