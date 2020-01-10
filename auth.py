
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, decode, encode
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import db_session
from db.models import User
from forms.auth import TokenPayload

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
TOKEN_SUBJECT = "access"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
USERS = {}
PRODUCTS = []


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/me/signin")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(s: Session, login: str):
    s.expire_on_commit = False
    return s.query(User).filter_by(email=login).first()


def authenticate_user(s: Session, login: str, password: str) -> User:
    user = get_user(s, login)
    return user if user and verify_password(password, user.hashed_password) else False


def create_access_token(*, data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": TOKEN_SUBJECT})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Security(oauth2_scheme),
        s: Session = Depends(db_session)) -> User:
    """Returns current user."""
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_user(s, login=token_data.login)
    return user if user else None


async def get_current_active_user(
        current_user: User = Depends(get_current_user)):
    """Return current active user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
