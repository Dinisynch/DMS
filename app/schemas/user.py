from pydantic import BaseModel, EmailStr, Field


class SUserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)


class SUserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)