import re
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, model_validator


def validate_password(v: str) -> str:
    errors = []

    if len(v) < 8:
        errors.append("не менее 8 символов")

    if re.search(r'[^A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', v):
        errors.append("только латинские буквы, цифры и специальные символы")

    if not re.search(r"[A-Z]", v):
        errors.append("хотя бы одну заглавную латинскую букву")

    if not re.search(r"[a-z]", v):
        errors.append("хотя бы одну строчную латинскую букву")

    if not re.search(r"\d", v):
        errors.append("хотя бы одну цифру")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', v):
        errors.append("хотя бы один специальный символ")

    if errors:
        raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")

    return v


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr


class UserResponse(UserBase):
    username: str | None = None
    roles: list[str] = []

    model_config = {"from_attributes": True}


class UserResponseWithId(UserBase):
    uuid: UUID
    username: str | None = None
    roles: list[str] = []

    model_config = {"from_attributes": True}


class UserSignupRequest(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: str) -> str:
        return validate_password(v)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password")
    @classmethod
    def password_validator(cls, v: str) -> str:
        return validate_password(v)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError("New passwords don't match")
        return self


class ChangePasswordResponse(BaseModel):
    msg: str


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None


class UpdateUserByAdminRequest(UserBase):
    new_email: EmailStr | None = None
    username: str | None = None
    roles: list[UserRole] | None = None


class DeleteUserByAdminResponse(BaseModel):
    msg: str
