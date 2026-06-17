from enum import StrEnum
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class BaseUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: PhoneNumber


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterUserSchema(BaseUserSchema):
    password: str


class CreateUserSchema(BaseUserSchema):
    password_hash: bytes


class RolesEnum(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"


class RoleSchema(BaseModel):
    id: int
    name: RolesEnum
    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseUserSchema):
    id: int
    role: RoleSchema
    model_config = ConfigDict(from_attributes=True)


class UserVerifySchema(BaseModel):
    pass
