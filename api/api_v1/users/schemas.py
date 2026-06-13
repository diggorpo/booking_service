from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class BaseUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: PhoneNumber
    role: str


class UserCreationSchema(BaseModel):
    password: str


class UserResponseSchema(BaseUserSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)
