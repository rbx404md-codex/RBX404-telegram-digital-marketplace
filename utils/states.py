from aiogram.fsm.state import State, StatesGroup


class CouponInput(StatesGroup):
    waiting_code = State()


class AdminAddCategory(StatesGroup):
    waiting_name = State()


class AdminAddProduct(StatesGroup):
    waiting_category = State()
    waiting_name = State()
    waiting_description = State()
    waiting_price_coin = State()
    waiting_price_stars = State()
    waiting_file = State()  # admin forwards/sends file here -> bot copies to storage channel
    waiting_preview = State()  # optional preview/sample file, or /skip


class AdminCoin(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()


class AdminCoupon(StatesGroup):
    waiting_code = State()
    waiting_type = State()
    waiting_value = State()
    waiting_limit = State()


class AdminBan(StatesGroup):
    waiting_user_id = State()
