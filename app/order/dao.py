from app.database.base_dao import BaseDAO
from app.database.models import Order
from app.database.models.order_model import OrderItem


class OrderDAO(BaseDAO):
    model = Order


class OrderItemDAO(BaseDAO):
    model = OrderItem
