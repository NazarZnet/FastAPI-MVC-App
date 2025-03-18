import os
from dotenv import load_dotenv


load_dotenv()

# JWT Security Settings
SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Access token expiry time in minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token expiry time in days

# Token Blacklisting
BLACKLISTED_TOKENS_EXPIRY = 86400  # 24 hours

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Redis Settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
USER_CACHE_EXPIRE = 900  # Cache expiration for users (15 minutes)
POST_CACHE_EXPIRE = 300  # Cache expiration for posts (5 minutes)

# Password Validation (Regex Pattern)
PASSWORD_REGEX = r"^[A-Za-z\d]+$"

# Maximum Post Size (1MB)
MAX_POST_SIZE_BYTES = 1_048_576
