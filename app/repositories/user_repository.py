from app.db.session import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Depends
from app.models.users import User
from schemas.user import UserCreate, UserUpdate


class UserRepository:
    @staticmethod
    async def search_user_by_email(email:str, db: AsyncSession=Depends(get_db())) -> User | None:
        result = select(User).where(User.email == email)
        return await result.scalar_one_or_none()

    @staticmethod
    async def search_user_by_id(id:int, db:AsyncSession=Depends(get_db)) -> User | None:
        result = select(User).where(User.id==id)
        return await result.scalar_one_or_none()

    @staticmethod
    async def create_user(user: UserCreate, db:AsyncSession=Depends(get_db)):
        new_user = User(name=user.name, 
                        email=user.email)

        try:
            db.add(new_user)
            db.commit(new_user)
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()

    @staticmethod
    async def update_user(user_id:str, user: UserUpdate, db:AsyncSession=Depends(get_db)):
        user = db.get(User, user_id)

        update_data = user.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

        except IntegrityError:
            db.rollback()

        return user


    





    