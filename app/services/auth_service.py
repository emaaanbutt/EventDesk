from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Depends
from app.core.exceptions import EmailAlreadyExistsError
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.db.session import get_db


async def duplicate_email(email:str, users:list[User], db:AsyncSession=Depends(get_db)):
        
        for user in users:
                if email == user.email:
                        return EmailAlreadyExistsError()

