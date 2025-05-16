from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.schemas.user import SUserRegister, SUserAuth, SUserOut
from app.core.security import get_password_hash, authenticate_user
from app.core.jwt import create_access_token, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register/")
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session)) -> dict:
    stmt = select(User).where(User.email == user_data.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже существует"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(**user_data.model_dump(exclude={"password"}), password=hashed_password)

    try:
        session.add(new_user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )

    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(user_data.email, user_data.password, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}


@router.get("/me/", response_model=SUserOut)
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}