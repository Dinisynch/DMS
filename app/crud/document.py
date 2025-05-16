from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from sqlalchemy import select
import io


from app.models.document import Document
from app.schemas.document import SDocumentCreate, SDocumentUpdate
from app.core.config import settings
from app.core.minio_client import minio_client


async def create_document(
    data: SDocumentCreate,
    user_id: int,
    session: AsyncSession,
    file: UploadFile | None = None
) -> Document:
    file_path = None
    if file is not None:
        content = await file.read()
        data_stream = io.BytesIO(content)
        object_name = f"{user_id}/{file.filename}"
        minio_client.put_object(
            bucket_name=settings.minio_bucket_name,
            object_name=object_name,
            data=data_stream,
            length=len(content),
            content_type=file.content_type,
        )
        file_path = object_name

    new_doc = Document(
        title=data.title,
        content=data.content,
        owner_id=user_id,
        file_path=file_path
    )
    session.add(new_doc)
    await session.commit()
    await session.refresh(new_doc)
    return new_doc


async def get_document(doc_id: int, session: AsyncSession) -> Document | None:
    stmt = select(Document).where(Document.id == doc_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_documents(user_id: int, session: AsyncSession) -> list[Document]:
    stmt = select(Document).where(Document.owner_id == user_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_document(
    document: Document,
    data: SDocumentUpdate,
    session: AsyncSession,
    file: UploadFile | None = None
) -> Document:
    if file is not None:
        content = await file.read()
        data_stream = io.BytesIO(content)
        object_name = f"{document.owner_id}/{file.filename}"
        minio_client.put_object(
            bucket_name=settings.minio_bucket_name,
            object_name=object_name,
            data=data_stream,
            length=len(content),
            content_type=file.content_type,
        )
        document.file_path = object_name

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(document, key, value)
    await session.commit()
    await session.refresh(document)
    return document


async def delete_document(document: Document, session: AsyncSession):
    if document.file_path:
        try:
            minio_client.remove_object(
                bucket_name=settings.minio_bucket_name,
                object_name=document.file_path
            )
        except Exception as e:
            print(f"Ошибка при удалении файла из MinIO: {e}")

    await session.delete(document)
    await session.commit()