import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import get_db
from models.orm import Product
from models.schemas import ProductOut, ProductListResponse

logger = logging.getLogger("products")

router = APIRouter(prefix="/products", tags=["Товары"])


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Список товаров с фильтрацией",
    description=(
        "Возвращает каталог букетов. Все параметры опциональны — "
        "без них возвращаются все активные товары."
    ),
)
async def get_products(
    # Фильтры — точно соответствуют FilterState из types/index.ts
    category: Optional[str] = Query(
        default=None,
        description="Категория: Романтика | День рождения | Свадьба | Корпоратив | Просто так",
        examples=["Романтика"]
    ),
    color: Optional[str] = Query(
        default=None,
        description="Цвет: Красный | Розовый | Белый | Жёлтый | Смешанный | Фиолетовый"
    ),
    size: Optional[str] = Query(
        default=None,
        description="Размер: Маленький | Средний | Большой"
    ),
    min_price: Optional[float] = Query(
        default=None, ge=0, description="Минимальная цена"
    ),
    max_price: Optional[float] = Query(
        default=None, ge=0, description="Максимальная цена"
    ),
    db: AsyncSession = Depends(get_db),
):
    # Строим запрос с фильтрами на уровне SQL
    conditions = [Product.is_active == True]  # noqa: E712

    if category and category != "Все":
        conditions.append(Product.category == category)
    if color and color != "Все":
        conditions.append(Product.color == color)
    if size and size != "Все":
        conditions.append(Product.size == size)
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)

    stmt = select(Product).where(and_(*conditions)).order_by(Product.id)
    result = await db.execute(stmt)
    products = result.scalars().all()

    # Собираем информацию о применённых фильтрах для дебага
    filters_applied = {
        k: v for k, v in {
            "category": category,
            "color": color,
            "size": size,
            "min_price": min_price,
            "max_price": max_price,
        }.items() if v is not None
    }

    logger.info(
        "GET /products: найдено %d товаров, фильтры: %s",
        len(products), filters_applied
    )

    return ProductListResponse(
        items=[ProductOut.model_validate(p) for p in products],
        total=len(products),
        filters_applied=filters_applied,
    )


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Детальная карточка товара",
    responses={404: {"description": "Товар не найден"}},
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(
        Product.id == product_id,
        Product.is_active == True  # noqa: E712
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        logger.warning("GET /products/%d: товар не найден", product_id)
        raise HTTPException(status_code=404, detail=f"Товар с id={product_id} не найден")

    return ProductOut.model_validate(product)