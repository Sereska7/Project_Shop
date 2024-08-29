from fastapi import APIRouter, HTTPException, Depends
from pydantic import parse_obj_as

from app.basket.dao import BasketDAO, BasketItemDAO
from app.database.models.order_model import PaymentType, OrderItem
from app.order.dao import OrderDAO, OrderItemDAO
from app.order.schemas import OrderRead
from app.product.dao import ProductDAO
from app.tasks.tasks import send_order_confirmation_email
from app.user.dependencies import get_current_user
from app.user.schemas import UserRead


route_buy = APIRouter(prefix="/buy", tags=["Buy"])


@route_buy.post("/items")
async def purchase_items(
    payment_method: PaymentType, user: UserRead = Depends(get_current_user)
):
    """
    Эта функция обрабатывает покупку всех товаров, находящихся в корзине пользователя.
    Если в корзине нет товаров или запрашиваемое количество товара превышает его наличие на складе,
    возвращает соответствующую ошибку.
    """
    basket = await BasketDAO.find_one_or_none(user_id=user.id)
    basket_items = await BasketItemDAO.find_all(basket_id=basket.id)
    if not basket_items:
        raise HTTPException(status_code=404, detail="Корзина пуста")

    total_price = 0
    lst_basket_items = []

    # Обрабатываем каждый товар в корзине
    for item in basket_items:
        product = await ProductDAO.find_one_or_none(id=item.product_id)

        # Если продукт не найден, возвращаем ошибку 404
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Продукт с ID {item.product_id} не найден"
            )

        # Если количество товара на складе недостаточно, возвращаем ошибку 400
        if product["quantity"] < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"Недостаточно товара {product.name} на складе"
            )

        # Считаем общую стоимость товаров в корзине
        total_price += item.price * item.quantity

        # Создаем объект для нового элемента заказа
        basket_item = OrderItem(
            basket_id=item.basket_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
        )
        lst_basket_items.append(basket_item)

    # Создаем новый заказ в базе данных
    order = await OrderDAO.add(
        user_id=user.id,
        total_price=total_price,
        status="completed",
        payment_method=payment_method,
    )

    # Добавляем товары из корзины в новый заказ
    for item in lst_basket_items:
        order_items = await OrderItemDAO.add(
            basket_id=item.basket_id,
            product_id=item.product_id,
            order_id=order["id"],
            quantity=item.quantity,
            price=item.price,
        )

    # Обновляем количество товара на складе после покупки
    for item in lst_basket_items:
        product = await ProductDAO.find_one_or_none(id=item.product_id)
        update_quantity = await ProductDAO.update(
            item.product_id, quantity=product.quantity - item.quantity
        )

    # Очищаем корзину пользователя после завершения покупки
    await BasketItemDAO.delete(basket_id=basket.id)

    # Извлекаем информацию о заказе и отправляем подтверждение по электронной почте
    order = await OrderDAO.find_one_or_none(id=order["id"])
    order_dict = parse_obj_as(OrderRead, order).dict()
    send_order_confirmation_email.delay(order_dict, user.email)

    return order
