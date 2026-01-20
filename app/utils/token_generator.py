from fastapi import HTTPException, Request
from dotenv import load_dotenv
from pathlib import Path
import os
import datetime
import jwt

# Load environment variables from .env file
#load_dotenv()

env_path = Path(__file__).resolve().parents[2] / ".env"

print("[INFO] Trying to load:", env_path)
print("[INFO] Exists:", env_path.exists())

load_dotenv(dotenv_path=env_path)
print("[INFO] SECRET_KEY from env:", os.getenv("SECRET_KEY"))
# Get the SECRET_KEY from environment
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Raise error if key not set
if not SECRET_KEY:
    raise ValueError("[ERROR] SECRET_KEY is not set in the environment variables.")

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    """
    Generate a JWT token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """
    Decode and verify the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_token_from_header(request: Request):
    """
    Extract token from the Authorization header and verify it.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    token = auth_header.split(" ")[1]
    return verify_access_token(token)

def require_auth(request: Request):
    """
    Wrapper for protected routes that extracts and validates JWT token.
    """
    return get_token_from_header(request)
