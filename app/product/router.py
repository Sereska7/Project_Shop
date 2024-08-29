import asyncio
from fastapi import APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache

from app.product.dao import ProductDAO
from app.product.schemas import ProductRead

router_product = APIRouter(prefix="/product", tags=["Product"])


@router_product.get("/get_all_products")
@cache(expire=30)
async def get_products(
    limit: int = Query(5, description="Number of products to return"),
    offset: int = Query(0, description="Number of products to skip"),
) -> list[ProductRead]:
    return await ProductDAO.find_all_products(limit, offset)


@router_product.get("/get_product/{product_id}")
@cache(expire=30)
async def get_product(product_id: int) -> ProductRead:
    """
    Эта функция извлекает информацию о товаре по его идентификатору. Если товар не найден,
    возвращается ошибка 404. Результат кэшируется на 30 секунд для оптимизации производительности.
    """
    product = await ProductDAO.find_one_or_none(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


@router_product.get("/by_category/{category_id}")
@cache(expire=30)
async def get_products_by_category(category_id: int) -> list[ProductRead]:
    """
    Эта функция извлекает все товары, относящиеся к указанной категории,
    на основе идентификатора категории. Результат кэшируется на 30 секунд
    для оптимизации производительности.
    """
    products = await ProductDAO.find_all(category_id=category_id)
    return products
