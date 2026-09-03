from aiogram import Router

from handlers import common, start, store, checkout, wallet, referral, orders
from handlers.admin import admin_router

root_router = Router(name="root")
root_router.include_router(common.router)
root_router.include_router(start.router)
root_router.include_router(store.router)
root_router.include_router(checkout.router)
root_router.include_router(wallet.router)
root_router.include_router(referral.router)
root_router.include_router(orders.router)
root_router.include_router(admin_router)
