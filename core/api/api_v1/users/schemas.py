from pydantic import BaseModel, EmailStr


class UserCreationSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
