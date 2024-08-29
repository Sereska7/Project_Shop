from sqladmin import ModelView

from app.database.models import User, Product, Category, Order, OrderItem
from app.database.models import BasketItem, Basket


class UserAdmin(ModelView, model=User):
    column_list = [User.email, User.id] + [User.basket]
    column_details_exclude_list = [User.hash_password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class BasketAdmin(ModelView, model=Basket):
    column_list = [Basket.id, Basket.user_id] + [Basket.user]
    column_details_exclude_list = [Basket.order_items]
    can_delete = False
    name = "Корзина"
    name_plural = "Корзины"
    icon = "fa-solid fa-basket"


class BasketItemAdmin(ModelView, model=BasketItem):
    column_list = [c.name for c in BasketItem.__table__.c] + [BasketItem.basket]
    column_details_exclude_list = [BasketItem.basket_id, Basket.order_items]
    can_delete = False
    name = "В корзине"
    name_plural = "В корзине"
    icon = "fa-solid fa-basket_item"


class ProductAdmin(ModelView, model=Product):
    column_list = [c.name for c in Product.__table__.c] + [Category.name]
    column_details_exclude_list = [Product.items, Product.category_id]
    name = "Продукт"
    name_plural = "Продукты"
    icon = "fa-solid fa-product"


class OrderAdmin(ModelView, model=Order):
    column_list = [c.name for c in Order.__table__.c] + [Order.user]
    can_delete = False
    can_edit = False
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-order"


class OrderItemsAdmin(ModelView, model=OrderItem):
    column_list = [c.name for c in OrderItem.__table__.c] + [
        OrderItem.basket,
        OrderItem.product,
        OrderItem.order,
    ]
    column_details_exclude_list = [OrderItem.basket_id, OrderItem.product_id]
    can_delete = False
    can_edit = False
    name = "Проданые товары"
    name_plural = "Проданые товары"
    icon = "fa-solid fa-orderitems"
