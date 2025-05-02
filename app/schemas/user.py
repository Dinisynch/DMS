from pydantic import BaseModel, EmailStr, Field


class SUserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия, от 1 до 50 символов")


class SUserAuth(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5, max_length=50)