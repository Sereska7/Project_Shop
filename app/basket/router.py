from typing import Optional

from fastapi import APIRouter, HTTPException, Depends

from app.basket.dao import BasketDAO, BasketItemDAO
from app.basket.schemas import BasketItemRead, BasketItemMiniRead
from app.product.dao import ProductDAO
from app.user.dependencies import get_current_user
from app.user.schemas import UserRead

router_basket = APIRouter(prefix="/basket", tags=["Basket"])


@router_basket.post("/add_in_basket/{product_id}")
async def add_in_basket(
    product_id: int, quantity: int = 1, user: UserRead = Depends(get_current_user)
) -> BasketItemRead:
    """
    Эта функция добавляет указанный товар в корзину пользователя. Если товар уже
    находится в корзине, увеличивает его количество. Если товара на складе недостаточно,
    возвращает ошибку.
    """
    basket = await BasketDAO.find_one_or_none(user_id=user.id)
    product = await ProductDAO.find_one_or_none(id=product_id)

    # Если продукт не найден, возвращаем ошибку 404
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # Если запрашиваемое количество товара превышает его наличие на складе, возвращаем ошибку 400
    if product.quantity <= quantity:
        raise HTTPException(
            status_code=400, detail=f"Недостаточно товара {product.name} на складе"
        )

    # Ищем элемент корзины, который соответствует данному товару и корзине пользователя
    basket_item = await BasketItemDAO.find_one_or_none(
        basket_id=basket.id, product_id=product.id
    )

    # Если элемент корзины не найден, создаем новый элемент
    if not basket_item:
        new_basket_item = await BasketItemDAO.add(
            basket_id=basket.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
        )
        # Возвращаем созданный элемент корзины
        return await BasketItemDAO.find_one_or_none(id=new_basket_item["id"])
    else:
        # Если элемент корзины уже существует, проверяем,
        # хватает ли товара на складе для добавления количества
        if product.quantity >= basket_item.quantity + quantity:
            # Обновляем количество товара в корзине
            update_quantity = await BasketItemDAO.update(
                basket_item.id, quantity=basket_item.quantity + quantity
            )
            # Возвращаем обновленный элемент корзины
            return await BasketItemDAO.find_one_or_none(id=update_quantity["id"])
        else:
            # Если товара не хватает, возвращаем ошибку 400
            raise HTTPException(
                status_code=400, detail=f"Недостаточно товара {product.name} на складе"
            )


@router_basket.get("/get_basket_items")
async def get_items_from_basket(user: UserRead = Depends(get_current_user)):
    """
    Эта функция извлекает все товары из корзины текущего пользователя,
    рассчитывает общую суммуи возвращает список товаров с информацией о каждом товаре.
    """
    basket = await BasketDAO.find_one_or_none(user_id=user.id)
    basket_items = await BasketItemDAO.find_all(basket_id=basket.id)

    # Рассчитываем общую сумму всех товаров в корзине
    total_price = sum(item.price * item.quantity for item in basket_items)

    # Создаем список объектов, содержащих информацию о товарах в корзине
    basket_items_read = [
        BasketItemMiniRead(
            product_name=(await ProductDAO.find_one_or_none(id=item.product_id)).name,
            quantity=item.quantity,
            price=item.price,
        )
        for item in basket_items
    ]

    # Возвращаем список товаров в корзине и общую сумму
    return {"basket_items": basket_items_read, "total_price": total_price}


@router_basket.patch("/decrease_quantity/{basket_item_id}")
async def decrease_quantity(
    product_id: int, quantity: int = 1, user: UserRead = Depends(get_current_user)
) -> Optional[BasketItemRead]:
    """
    Эта функция уменьшает количество указанного товара в корзине пользователя.
    Если количество уменьшается до нуля или ниже, товар удаляется из корзины.
    """
    basket = await BasketDAO.find_one_or_none(user_id=user.id)
    basket_item = await BasketItemDAO.find_one_or_none(
        product_id=product_id, basket_id=basket.id
    )
    if basket_item is None:
        raise HTTPException(status_code=404, detail="Товар в корзине не найден")
        # Рассчитываем новое количество товара после уменьшения
    new_quantity = basket_item.quantity - quantity

    # Если новое количество меньше или равно нулю, удаляем товар из корзины
    if new_quantity <= 0:
        await BasketItemDAO.delete(product_id=product_id, basket_id=basket.id)
        return None  # Возвращаем None, чтобы указать, что товар был удален
    else:
        # Если количество товара все еще положительное, обновляем его в базе данных
        update_quantity = await BasketItemDAO.update(
            basket_item.id, quantity=new_quantity
        )
        # Возвращаем обновленный элемент корзины
        return await BasketItemDAO.find_one_or_none(id=update_quantity["id"])


@router_basket.delete("/delete_from_basket/{product_id}")
async def delete_in_basket(product_id: int, user: UserRead = Depends(get_current_user)):
    """
    Эта функция удаляет товар из корзины пользователя.
    """
    basket = await BasketDAO.find_one_or_none(user_id=user.id)
    product = await BasketItemDAO.find_one_or_none(
        product_id=product_id, basket_id=basket.id
    )
    if not product:
        raise HTTPException(status_code=404, detail="В корзине нет такого продукта")
    await BasketItemDAO.delete(product_id=product_id, basket_id=basket.id)
    return {"process": True}
