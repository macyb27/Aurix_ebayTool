"""Products API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Produkt erstellen."""
    from sqlalchemy import select
    from app.models.product import Product

    product = Product(
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        brand=data.brand,
        condition=data.condition,
        suggested_price=data.suggested_price,
        image_url=data.image_url,
        user_id=data.user_id or user_id,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Produkt abrufen."""
    from sqlalchemy import select
    from app.models.product import Product

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Produkt aktualisieren."""
    from sqlalchemy import select
    from app.models.product import Product

    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await db.flush()
    await db.refresh(product)
    return product
