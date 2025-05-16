from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class SDocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок документа")
    content: Optional[str] = Field(None, description="Текстовое содержимое документа")


class SDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Обновлённый заголовок")
    content: Optional[str] = Field(None, description="Обновлённое содержимое")


class SDocumentRead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    file_url: Optional[HttpUrl]

    class Config:
        from_attributes = True