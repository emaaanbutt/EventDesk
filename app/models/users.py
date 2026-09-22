from sqlalchemy import Integer, String, VARCHAR, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimeStamp
from enums import Role

class User(Base, TimeStamp):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(100))
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
