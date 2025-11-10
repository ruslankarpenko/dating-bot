from aiogram import F, types
from aiogram.fsm.context import FSMContext
import logging
import asyncio

from database import connect_db
from keyboards import get_admin_keyboard
from states import AdminStates

async def admin_menu(message: types.Message):
    if message.from_user.id != 6346589919:
        await message.answer("У вас немає прав для виконання цієї команди.")
        return
    await show_admin_menu(message.from_user.id)

async def show_admin_menu(chat_id: int):
    await Bot.get_current().send_message(
        chat_id=chat_id,
        text="Адмін-меню:",
        reply_markup=get_admin_keyboard()
    )

async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != 6346589919:
        return
    
    await message.answer("Надішліть повідомлення для розсилки (текст, фото або відео):", 
                       reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AdminStates.broadcast_message)

# ... (інші адмін-функції з вашого коду)