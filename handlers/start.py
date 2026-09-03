from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile
import os

from database.queries import get_or_create_user, get_user
from utils.keyboards import main_menu
from utils.ui import safe_edit

router = Router(name="start")

WELCOME_TEXT = (
    "👋 স্বাগতম {name}!\n\n"
    "এটি আমাদের ডিজিটাল স্টোর বট — এখান থেকে পেইড ভিডিও, ফাইল, ডকুমেন্ট কিনতে পারবেন "
    "🪙 কয়েন অথবা ⭐ Telegram Stars দিয়ে।\n\n"
    "👇 নিচের মেনু থেকে শুরু করুন।"
)
WELCOME_IMAGE_PATH = "assets/welcome.jpg"  # optional — admin can replace this file


async def send_welcome(message: Message, name: str) -> None:
    text = WELCOME_TEXT.format(name=name)
    if os.path.exists(WELCOME_IMAGE_PATH):
        await message.answer_photo(FSInputFile(WELCOME_IMAGE_PATH), caption=text, reply_markup=main_menu())
    else:
        await message.answer(text, reply_markup=main_menu())


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    ref_code = command.args.strip() if command.args else None
    user = await get_or_create_user(message.from_user.id, message.from_user.username, ref_code)

    if user["is_banned"]:
        await message.answer("🚫 আপনি এই বট ব্যবহার করা থেকে নিষিদ্ধ।")
        return

    await send_welcome(message, message.from_user.first_name or "বন্ধু")


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery) -> None:
    await safe_edit(
        callback,
        WELCOME_TEXT.format(name=callback.from_user.first_name or "বন্ধু"),
        reply_markup=main_menu(),
    )
    await callback.answer()
