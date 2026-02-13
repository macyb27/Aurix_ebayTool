"""Pricing History Model."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class PricingHistory(Base, TimestampMixin):
    """Historische Preisdaten für Analyse."""

    __tablename__ = "pricing_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True, index=True
    )
    category_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    search_query: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avg_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    max_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
