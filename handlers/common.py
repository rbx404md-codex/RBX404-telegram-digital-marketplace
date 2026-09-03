from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name="common")


@router.message(Command("cancel"))
async def cancel_any_flow(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("কোনো চলমান কাজ নেই।")
        return
    await state.clear()
    await message.answer("❌ বাতিল করা হয়েছে।")
