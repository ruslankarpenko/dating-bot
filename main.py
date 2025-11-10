import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram import BaseMiddleware
from aiogram.filters import CommandStart  # Добавьте эту строку
from typing import Callable, Dict, Any, Awaitable, Union
from datetime import datetime, timezone

from database import init_db
from handlers.start import cmd_start, start_creation, show_existing_profile
from handlers.profile import process_name, process_age, process_city, process_gender, wrong_gender, process_bio, process_photo
from handlers.search import process_search_gender, wrong_search_gender, process_search_age_min, process_search_age_max, handle_action
from handlers.common import show_next_profile
from handlers.admin import admin_menu, start_broadcast
from states import ProfileStates
from texts import texts
from keyboards import get_menu_keyboard

API_TOKEN = ''
bot_start_time = datetime.now(timezone.utc)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

class MessageTimeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        event_date = None

        if isinstance(event, types.Message):
            event_date = event.date
        elif isinstance(event, types.CallbackQuery) and event.message:
            event_date = event.message.date

        if event_date and event_date < bot_start_time:
            logging.info(f"Ignoring message from {event.from_user.id} sent before bot start")
            return

        return await handler(event, data)

# Реєстрація middleware
dp.message.middleware(MessageTimeMiddleware())
dp.callback_query.middleware(MessageTimeMiddleware())

# Реєстрація хендлерів
dp.message.register(cmd_start, CommandStart())
dp.message.register(start_creation, F.text == "Ок")
dp.message.register(start_creation, F.text == "Створити")
dp.message.register(show_existing_profile, F.text == "У мене вже є анкета")

# Хендлери профілю
dp.message.register(process_name, ProfileStates.name)
dp.message.register(process_age, ProfileStates.age)
dp.message.register(process_city, ProfileStates.city)
dp.message.register(process_gender, ProfileStates.gender, F.text.in_(["👨 Чоловік", "👩 Жінка"]))
dp.message.register(wrong_gender, ProfileStates.gender)
dp.message.register(process_bio, ProfileStates.bio)
dp.message.register(process_photo, ProfileStates.photo)

# Хендлери пошуку
dp.message.register(process_search_gender, ProfileStates.search_gender, F.text.in_(["👨 Чоловіка", "👩 Жінку", "🔹 Обох"]))
dp.message.register(wrong_search_gender, ProfileStates.search_gender)
dp.message.register(process_search_age_min, ProfileStates.search_age_min)
dp.message.register(process_search_age_max, ProfileStates.search_age_max)
dp.message.register(handle_action, F.text.in_(["❤️ Вподобати", "⏭ Пропустити", "📋 Меню"]))

# Адмін-хендлери
dp.message.register(admin_menu, F.text == "/admin")
dp.message.register(start_broadcast, F.text == "📢 Розсилка")

# Інші хендлери
dp.message.register(lambda m: show_next_profile(m.from_user.id), F.text == "👀 Дивитись анкети")
dp.message.register(lambda m: m.answer("Меню:", reply_markup=get_menu_keyboard()), F.text == "🔙 Назад")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
