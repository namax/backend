from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Schema


class SignUp(BaseModel):
    login: str
    password: str
    name: str
    promocode: Optional[str]


class SignIn(OAuth2PasswordRequestForm):
    pass


class UserInfo(BaseModel):
    name: str = Schema(
        "", title="User's name",
    )
    email: str = ""
    disabled: bool = False
