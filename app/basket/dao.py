from app.database.base_dao import BaseDAO
from app.database.models import Basket
from app.database.models import BasketItem


class BasketDAO(BaseDAO):
    model = Basket


class BasketItemDAO(BasketDAO):
    model = BasketItem
