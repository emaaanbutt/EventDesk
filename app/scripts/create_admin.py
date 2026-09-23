"""Create the first admin: python -m app.scripts.create_admin --email EMAIL --name NAME"""

from __future__ import annotations

import argparse
import asyncio
from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.enums import Role
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import validate_password_strength


async def create_admin(email: str, name: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        active_admin = await db.scalar(
            select(User.id).where(
                User.role == Role.admin,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            ).limit(1)
        )
        if active_admin is not None:
            raise SystemExit("An active admin already exists. Use the role-change API instead.")
        if await UserRepository.get_by_email(email, db) is not None:
            raise SystemExit("That email already exists.")

        db.add(User(name=name, email=email, password_hash=hash_password(password),
                    role=Role.admin, is_active=True))
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise SystemExit("That email already exists.") from None
    print(f"Admin created: {email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first EventDesk admin")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    try:
        email = str(TypeAdapter(EmailStr).validate_python(args.email)).lower()
    except ValidationError:
        raise SystemExit("Enter a valid email address.") from None
    name = args.name.strip()
    if not 1 <= len(name) <= 100:
        raise SystemExit("Name must be 1–100 characters.")

    password = getpass("Admin password: ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match.")
    try:
        validate_password_strength(password)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None

    asyncio.run(create_admin(email, name, password))


if __name__ == "__main__":
    main()
