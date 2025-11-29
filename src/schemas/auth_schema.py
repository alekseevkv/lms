from pydantic import BaseModel, EmailStr


class SigninResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    msg: str
