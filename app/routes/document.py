from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.document import SDocumentCreate, SDocumentUpdate, SDocumentRead
from app.database import get_session
from app.core.jwt import get_current_user
from app.models.user import User
from app.crud import document as crud
from app.services.minio_service import build_file_url

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)


@router.post("/", response_model=SDocumentRead)
async def create_document(
    title: str = Form(..., min_length=1, max_length=255),
    content: str | None = Form(None),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    data = SDocumentCreate(title=title, content=content)
    return await crud.create_document(data, user.id, session, file=file)


@router.get("/", response_model=list[SDocumentRead])
async def read_user_documents(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    return await crud.get_user_documents(user.id, session)


@router.get("/{doc_id}/", response_model=SDocumentRead)
async def read_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    doc = await crud.get_document(doc_id, session)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Документ не найден")

    doc_data = SDocumentRead.model_validate(doc)
    doc_dict = doc_data.model_dump(exclude={"file_url"})
    return SDocumentRead(**doc_dict, file_url=build_file_url(doc))


@router.put("/{doc_id}/", response_model=SDocumentRead)
async def update_document(
    doc_id: int,
    title: str | None = Form(None, min_length=1, max_length=255),
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    doc = await crud.get_document(doc_id, session)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Документ не найден")
    data = SDocumentUpdate(title=title, content=content)
    return await crud.update_document(doc, data, session, file=file)


@router.delete("/{doc_id}/", status_code=204)
async def delete_document(
    doc_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    doc = await crud.get_document(doc_id, session)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Документ не найден")
    await crud.delete_document(doc, session)
