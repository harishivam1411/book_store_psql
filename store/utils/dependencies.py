from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from store.models.auth.auth_model import TokenPayload
from store.utils.util import validate_token

oauth2_bearer = HTTPBearer()

def validate_access_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_bearer)) -> TokenPayload:
    """Validate access token from Authorization header"""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is required")
    try:
        token_data = validate_token(credentials.credentials, "access token")
        if token_data.token_type != 'access':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only access tokens can be used for authentication")
        return token_data

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired")

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def validate_refresh_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_bearer)) -> TokenPayload:
    """Validate refresh token from Authorization header"""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")
    try:
        token_data = validate_token(credentials.credentials, "refresh token")
        if token_data.token_type != 'refresh':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only refresh tokens can be used for renewing access tokens")
        return token_data

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_current_user(token_data: TokenPayload = Depends(validate_access_token)) -> TokenPayload:
    """Get the current authenticated user from the token"""
    if not token_data.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data