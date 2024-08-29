import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis
from sqladmin import Admin

from app.admin.admin_auth import authentication_backend
from app.admin.views import (
    UserAdmin,
    BasketItemAdmin,
    ProductAdmin,
    BasketAdmin,
    OrderAdmin,
    OrderItemsAdmin,
)
from app.basket.router import router_basket
from app.database.base_db import engine
from app.order.router import route_buy
from app.product.router import router_product
from app.user.router import router_auth, router_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    # shutdown


main_app = FastAPI(lifespan=lifespan)

admin = Admin(main_app, engine=engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(BasketItemAdmin)
admin.add_view(ProductAdmin)
admin.add_view(BasketAdmin)
admin.add_view(OrderAdmin)
admin.add_view(OrderItemsAdmin)


main_app.include_router(router_auth)
main_app.include_router(router_user)
main_app.include_router(router_product)
main_app.include_router(router_basket)
main_app.include_router(route_buy)


if __name__ == "__main__":
    uvicorn.run("app.main:main_app", reload=True)
