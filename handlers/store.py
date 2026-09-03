from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from config import STORAGE_CHANNEL_ID
from database.queries import list_categories, list_products, get_product
from utils.keyboards import categories_kb, products_kb, product_detail_kb
from utils.ui import safe_edit

router = Router(name="store")


@router.callback_query(F.data == "store:categories")
async def show_categories(callback: CallbackQuery) -> None:
    cats = await list_categories()
    if not cats:
        await callback.answer("এখনো কোনো ক্যাটাগরি যোগ করা হয়নি।", show_alert=True)
        return
    await safe_edit(callback, "📂 একটি ক্যাটাগরি বেছে নিন:", reply_markup=categories_kb(cats))
    await callback.answer()


@router.callback_query(F.data.startswith("store:cat:"))
async def show_products(callback: CallbackQuery) -> None:
    category_id = int(callback.data.split(":")[2])
    products = await list_products(category_id=category_id)
    if not products:
        await callback.answer("এই ক্যাটাগরিতে এখনো কোনো প্রোডাক্ট নেই।", show_alert=True)
        return
    await safe_edit(callback, "🛍️ প্রোডাক্ট বেছে নিন:", reply_markup=products_kb(products, category_id))
    await callback.answer()


@router.callback_query(F.data.startswith("store:product:"))
async def show_product_detail(callback: CallbackQuery) -> None:
    product_id = int(callback.data.split(":")[2])
    p = await get_product(product_id)
    if not p or not p["is_active"]:
        await callback.answer("প্রোডাক্টটি খুঁজে পাওয়া যায়নি।", show_alert=True)
        return

    text = (
        f"📦 <b>{p['name']}</b>\n\n"
        f"{p['description']}\n\n"
        f"💰 দাম: 🪙 {p['price_coin']} কয়েন / ⭐ {p['price_stars']} Stars\n"
        f"🔥 বিক্রি হয়েছে: {p['sales_count']} বার"
    )
    await safe_edit(callback, text, reply_markup=product_detail_kb(product_id, has_preview=bool(p["preview_msg_id"])))
    await callback.answer()


@router.callback_query(F.data.startswith("store:preview:"))
async def send_preview(callback: CallbackQuery, bot: Bot) -> None:
    product_id = int(callback.data.split(":")[2])
    p = await get_product(product_id)
    if not p or not p["preview_msg_id"]:
        await callback.answer("এই প্রোডাক্টের কোনো প্রিভিউ নেই।", show_alert=True)
        return
    await bot.copy_message(
        chat_id=callback.from_user.id,
        from_chat_id=STORAGE_CHANNEL_ID,
        message_id=p["preview_msg_id"],
    )
    await callback.answer()
