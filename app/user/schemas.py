from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    email: EmailStr
    hash_password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr


class UserUpdate(UserCreate):
    pass
