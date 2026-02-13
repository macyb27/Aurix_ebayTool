"""AI-Analyse-Ergebnis Model."""

from sqlalchemy import Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class AIResult(Base, TimestampMixin):
    """Gespeichertes FullAIResult (JSON)."""

    __tablename__ = "ai_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    input_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    product_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
