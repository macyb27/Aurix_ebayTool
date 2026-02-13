"""Market Data Model für Trend-Analysen."""

from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class MarketData(Base, TimestampMixin):
    """Marktdaten und Trends."""

    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    search_term: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avg_sold_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    sold_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_listings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    demand_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
