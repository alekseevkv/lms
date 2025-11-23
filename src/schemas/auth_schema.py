from pydantic import BaseModel, EmailStr


class SigninResponse(BaseModel):
    access_token: str
    token_type: str


class Signin(BaseModel):
    email: EmailStr
    password: str
