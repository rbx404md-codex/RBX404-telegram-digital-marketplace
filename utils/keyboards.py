from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍️ Store", callback_data="store:categories")
    kb.button(text="🪙 Wallet", callback_data="wallet:open")
    kb.button(text="🎁 Referral", callback_data="referral:open")
    kb.button(text="📚 My Purchases", callback_data="orders:mine")
    kb.adjust(2, 2)
    return kb.as_markup()


def categories_kb(categories: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=f"{c['icon']} {c['name']}", callback_data=f"store:cat:{c['category_id']}")
    kb.button(text="⬅️ Back", callback_data="menu:main")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products: list[dict], category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p['name']} — 🪙{p['price_coin']} / ⭐{p['price_stars']}",
                   callback_data=f"store:product:{p['product_id']}")
    kb.button(text="⬅️ Back", callback_data="store:categories")
    kb.adjust(1)
    return kb.as_markup()


def product_detail_kb(product_id: int, has_preview: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if has_preview:
        kb.button(text="🔍 Preview দেখুন", callback_data=f"store:preview:{product_id}")
    kb.button(text="🪙 Buy with Coin", callback_data=f"buy:coin:{product_id}")
    kb.button(text="⭐ Buy with Stars", callback_data=f"buy:stars:{product_id}")
    kb.button(text="🎟️ I have a coupon", callback_data=f"buy:coupon:{product_id}")
    kb.button(text="⬅️ Back", callback_data="store:categories")
    if has_preview:
        kb.adjust(1, 2, 1, 1)
    else:
        kb.adjust(2, 1, 1)
    return kb.as_markup()


def wallet_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📜 Transaction History", callback_data="wallet:history")
    kb.button(text="➕ Top-up (Coin)", callback_data="wallet:topup")
    kb.button(text="⬅️ Back", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def admin_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Add Product", callback_data="admin:add_product")
    kb.button(text="📋 Manage Products", callback_data="admin:list_products")
    kb.button(text="📂 Add Category", callback_data="admin:add_category")
    kb.button(text="🪙 Add/Deduct Coin", callback_data="admin:coin")
    kb.button(text="🎟️ Create Coupon", callback_data="admin:add_coupon")
    kb.button(text="🚫 Ban / Unban", callback_data="admin:ban")
    kb.button(text="📊 Sales Stats", callback_data="admin:stats")
    kb.button(text="🗄 Backup Now", callback_data="admin:backup_now")
    kb.adjust(2)
    return kb.as_markup()


def admin_product_list_kb(products: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        status = "✅" if p["is_active"] else "🚫"
        kb.button(text=f"{status} {p['name']}", callback_data=f"admin:toggle_product:{p['product_id']}")
    kb.button(text="⬅️ Back", callback_data="admin:panel")
    kb.adjust(1)
    return kb.as_markup()
