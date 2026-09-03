from aiogram import Router

from handlers.admin import panel, product_manage, coin_manage, coupon_manage, user_manage

admin_router = Router(name="admin_root")
admin_router.include_router(panel.router)
admin_router.include_router(product_manage.router)
admin_router.include_router(coin_manage.router)
admin_router.include_router(coupon_manage.router)
admin_router.include_router(user_manage.router)
