"""API Dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


async def get_current_user_id() -> str:
    """Stub: User-ID aus Auth (JWT etc.). In Produktion ersetzen."""
    return "default-user"


def get_db_session():
    """Database Session Dependency - verwendet get_db direkt."""
    return get_db
