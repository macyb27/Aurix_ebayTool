"""Product Model - aus Vision-Analyse oder manuell."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Product(Base, TimestampMixin):
    """Produkt-Entität (Vision-Analyse oder manuell erstellt)."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(200), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suggested_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    vision_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    user_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
