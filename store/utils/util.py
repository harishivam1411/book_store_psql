import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from store.models.auth.auth_model import TokenPayload, TokenResponse

load_dotenv()
password_context = CryptContext(schemes=["argon2"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 300 
ALGORITHM = os.environ['ALGORITHM']
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']

def get_hashed_password(password: str) -> str:
    """Hash a password using Argon2"""
    return password_context.hash(password)

def verify_hashed_password(password: str, hashed_pass: str) -> bool:
    """Verify a password against its hash"""
    return password_context.verify(password, hashed_pass)

def generate_tokens(user_id: str) -> TokenResponse:
    """Generate access and refresh tokens for a user"""
    return TokenResponse(
        access_token = create_access_token({"user_id": user_id, "token_type": "access"}),
        refresh_token = create_refresh_token({"user_id": user_id, "token_type": "refresh"})
    )

def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration time"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration time"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def validate_token(token: str, token_type: str) -> TokenPayload:
    """Validate a JWT token and return the token data"""
    try:
        # Use the correct secret key based on token type
        key = JWT_REFRESH_SECRET_KEY if token_type == "refresh token" else JWT_SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        token_data = TokenPayload(
            user_id=payload["user_id"],
            exp=datetime.fromtimestamp(payload["exp"], timezone.utc),
            token_type=payload["token_type"],
            valid=True
        )
        return token_data
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{token_type} expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token, {token_type}")