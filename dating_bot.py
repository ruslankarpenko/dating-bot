import asyncio
import logging
import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command, CommandStart
from aiogram.client.default import DefaultBotProperties

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

class ProfileStates(StatesGroup):
    name = State()
    age = State()
    city = State()
    gender = State()
    bio = State()
    photo = State()
    search_gender = State()
    search_age_min = State()
    search_age_max = State()
    edit_search_gender = State()
    edit_search_age_min = State()
    edit_search_age_max = State()

texts = {
    'greeting': "Привіт, я допоможу тобі знайти пару чи просто друзів !",
    'start': "Давай створимо твій профіль.\nЯк тебе звати?",
    'age': "Скільки тобі років?",
    'city': "З якого ти міста?",
    'gender': "Виберіть свій стать:",
    'bio': "Напишіть трохи про себе:",
    'photo': "Надішліть своє фото:",
    'created': "Профіль створено! Показую людей поруч 🔍",
    'no_profiles': "Поки більше анкет немає. Спробуйте пізніше 🙃",
    'match': "🎉 У вас є співпадіння!",
    'search_stopped': "Пошук зупинено",
    'no_new_likes': "Немає нових вподобань.",
    'edit_search_criteria': "Редагуйте критерії пошуку.",
    'deactivated': "Ваша анкета була деактивована."
}

# Keyboard functions

def get_greeting_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ок")
    kb.button(text="У мене вже є анкета")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_reply_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="❤️ Вподобати")
    kb.button(text="⏭ Пропустити")
    kb.button(text="📋 Меню")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="✏️ Редагувати анкету")
    kb.button(text="👀 Дивитись анкети")
    kb.button(text="🔄 Редагувати критерії пошуку")
    kb.button(text="❌ Деактивувати анкету")
    return kb.as_markup(resize_keyboard=True)

def get_gender_keyboard_self():
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Чоловік")
    kb.button(text="👩 Жінка")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_gender_keyboard_search():
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Чоловік")
    kb.button(text="👩 Жінка")
    kb.button(text="🔹 Обидва")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# DB connection function
async def connect_db():
    return await aiosqlite.connect("dating.db")

# DB initialization
async def init_db():
    db = await connect_db()  # explicitly await the connection
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT,
            gender TEXT,
            bio TEXT,
            photo_id TEXT,
            search_gender TEXT,
            search_age_min INTEGER,
            search_age_max INTEGER,
            username TEXT
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            from_id INTEGER,
            to_id INTEGER,
            UNIQUE(from_id, to_id)
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS views (
            viewer_id INTEGER,
            viewed_id INTEGER,
            UNIQUE(viewer_id, viewed_id)
        )
    """)
    await db.commit()

# Start command
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    keyboard = get_greeting_keyboard()
    await message.answer(texts['greeting'], reply_markup=keyboard)

# Create profile flow
@dp.message(F.text == "Ок")
async def start_creation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts['start'])
    await state.set_state(ProfileStates.name)

@dp.message(F.text == "У мене вже є анкета")
async def show_existing_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db = await connect_db()
    async with db.execute("SELECT name, age, city, gender, bio, photo_id, search_gender, search_age_min, search_age_max, username FROM users WHERE user_id = ?", (user_id,)) as cur:
        row = await cur.fetchone()

    if row:
        name, age, city, gender, bio, photo_id, search_gender, search_age_min, search_age_max, username = row
        text = f"*{name}*, {age}\n{city}\n{bio}"
        await bot.send_photo(user_id, photo_id, caption=text, reply_markup=get_menu_keyboard())
    else:
        await message.answer("У вас немає анкети.", reply_markup=get_menu_keyboard())

@dp.message(ProfileStates.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(texts['age'])
    await state.set_state(ProfileStates.age)

@dp.message(ProfileStates.age)
async def set_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Вік має бути числом.")
    await state.update_data(age=int(message.text))
    await message.answer(texts['city'])
    await state.set_state(ProfileStates.city)

@dp.message(ProfileStates.city)
async def set_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(texts['gender'], reply_markup=get_gender_keyboard_self())
    await state.set_state(ProfileStates.gender)

@dp.message(ProfileStates.gender)
async def set_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer(texts['bio'], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.bio)

@dp.message(ProfileStates.bio)
async def set_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    await message.answer(texts['photo'])
    await state.set_state(ProfileStates.photo)

@dp.message(F.photo, ProfileStates.photo)
async def set_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("Кого ви шукаєте за статтю?", reply_markup=get_gender_keyboard_search())
    await state.set_state(ProfileStates.search_gender)



@dp.message(ProfileStates.search_gender)
async def set_search_gender(message: Message, state: FSMContext):
    await state.update_data(search_gender=message.text)
    await message.answer("Введіть мінімальний вік партнера:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.search_age_min)

@dp.message(ProfileStates.search_age_min)
async def set_search_age_min(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Будь ласка, введіть число.")
    await state.update_data(search_age_min=int(message.text))
    await message.answer("Введіть максимальний вік партнера:")
    await state.set_state(ProfileStates.search_age_max)

@dp.message(ProfileStates.search_age_max)
async def set_search_age_max(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Будь ласка, введіть число.")
    
    search_age_max = int(message.text)
    data = await state.get_data()

    username = message.from_user.username if message.from_user.username else "Без username"

    db = await connect_db()
    await db.execute("""
        REPLACE INTO users (user_id, name, age, city, gender, bio, photo_id, search_gender, search_age_min, search_age_max, username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        message.from_user.id,
        data['name'],
        data['age'],
        data['city'],
        data['gender'],
        data['bio'],
        data['photo'],
        data['search_gender'],
        data['search_age_min'],
        search_age_max,
        username
    ))
    await db.commit()

    await message.answer(texts['created'], reply_markup=get_reply_keyboard())
    await state.clear()
    await show_next_profile(message.from_user.id)

# Show next profile
async def show_next_profile(user_id: int):
    db = await connect_db()
    async with db.execute(
        "SELECT city, search_gender, search_age_min, search_age_max FROM users WHERE user_id = ?",
        (user_id,)
    ) as cur:
        user_data = await cur.fetchone()

    if not user_data:
        return

    city, search_gender, age_min, age_max = user_data

    query = """
    SELECT user_id, name, age, city, gender, bio, photo_id, username FROM users
    WHERE user_id != ? 
    AND user_id NOT IN (SELECT viewed_id FROM views WHERE viewer_id = ?)
    AND (gender = ? OR ? = '🔹 Обидва')
    AND age BETWEEN ? AND ?
    ORDER BY city = ? DESC
    LIMIT 1
    """
    async with db.execute(query, (user_id, user_id, search_gender, search_gender, age_min, age_max, city)) as cur:
        row = await cur.fetchone()

    if row:
        uid, name, age, city, gender, bio, photo_id, username = row
        text = f"*{name}*, {age}\n{city}\n{bio}"
        await bot.send_photo(user_id, photo_id, caption=text, reply_markup=get_reply_keyboard())
        await db.execute("INSERT OR IGNORE INTO views VALUES (?, ?)", (user_id, uid))
        await db.commit()
    else:
        await bot.send_message(user_id, texts['no_profiles'], reply_markup=get_menu_keyboard())

# Like and View Actions
@dp.message(F.text.in_(["❤️ Вподобати", "⏭ Пропустити", "📋 Меню"]))
async def handle_action(message: Message):
    user_id = message.from_user.id

    if message.text == "📋 Меню":
        await message.answer("Оберіть дію:", reply_markup=get_menu_keyboard())
        return

    db = await connect_db()
    async with db.execute(
        "SELECT viewed_id FROM views WHERE viewer_id = ? ORDER BY rowid DESC LIMIT 1",
        (user_id,)
    ) as cur:
        row = await cur.fetchone()

    if not row:
        await message.answer(texts['no_profiles'], reply_markup=get_menu_keyboard())
        return

    to_user = row[0]

    if message.text == "❤️ Вподобати":
        await db.execute(
            "INSERT OR IGNORE INTO likes (from_id, to_id) VALUES (?, ?)",
            (user_id, to_user)
        )

        async with db.execute(
            "SELECT 1 FROM likes WHERE from_id = ? AND to_id = ?",
            (to_user, user_id)
        ) as check:
            is_mutual = await check.fetchone()

        if is_mutual:
            async with db.execute("SELECT name, username FROM users WHERE user_id = ?", (to_user,)) as c1:
                to_name, to_username = await c1.fetchone()
            async with db.execute("SELECT name, username FROM users WHERE user_id = ?", (user_id,)) as c2:
                from_name, from_username = await c2.fetchone()

            link1 = f"[{to_name}](tg://user?id={to_user}) / @{to_username}" if to_username else f"[{to_name}](tg://user?id={to_user})"
            link2 = f"[{from_name}](tg://user?id={user_id}) / @{from_username}" if from_username else f"[{from_name}](tg://user?id={user_id})"

            await bot.send_message(user_id, f"🎉 У вас є співпадіння! Напишіть одне одному: {link1}")
            await bot.send_message(to_user, f"🎉 У вас є співпадіння! Напишіть одне одному: {link2}")
        else:
            async with db.execute(
                "SELECT name, age, city, bio, photo_id FROM users WHERE user_id = ?",
                (user_id,)
            ) as cur2:
                liker = await cur2.fetchone()
                if liker:
                    name, age, city, bio, photo_id = liker
                    text = f"✨ Вас хтось вподобав!"
                    reply_markup = ReplyKeyboardBuilder().button(text="👀 Подивитись").button(text="⏭ Пропустити").as_markup(resize_keyboard=True)
                    await bot.send_message(
                        to_user,
                        text,
                        reply_markup=reply_markup
                    )
                    await db.execute(
                        "INSERT OR IGNORE INTO views (viewer_id, viewed_id) VALUES (?, ?)",
                        (to_user, user_id)
                    )

        await db.commit()

    await asyncio.sleep(0.5)
    await show_next_profile(user_id)
    await bot.send_photo(reply_markup=get_reply_keyboard())

@dp.message(F.text == "👀 Подивитись")
async def view_liked_profile(message: Message):
    user_id = message.from_user.id

    async with aiosqlite.connect("dating.db") as db:
        await db.execute("PRAGMA journal_mode=WAL")

        async with db.execute(
            "SELECT viewed_id FROM views WHERE viewer_id = ? ORDER BY rowid DESC LIMIT 1",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()

        if not row:
            await message.answer(texts['no_profiles'], reply_markup=get_menu_keyboard())
            return

        to_user = row[0]

        async with db.execute(
            "SELECT name, age, city, bio, photo_id FROM users WHERE user_id = ?",
            (to_user,)
        ) as cur:
            profile = await cur.fetchone()

        if profile:
            name, age, city, bio, photo_id = profile
            text = f"*{name}*, {age}\n{city}\n{bio}"
            await bot.send_photo(user_id, photo_id, caption=text, reply_markup=get_reply_keyboard())

    await db.commit()

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Оберіть дію:", reply_markup=get_menu_keyboard())

@dp.message(F.text == "✏️ Редагувати анкету")
async def edit_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts['start'], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ProfileStates.name)

@dp.message(F.text == "🔄 Редагувати критерії пошуку")
async def edit_search_criteria(message: Message, state: FSMContext):
    await message.answer("Зміни критерії пошуку:\n\nВиберіть цільовий стать:", reply_markup=get_gender_keyboard_search())
    await state.set_state(ProfileStates.edit_search_gender)

@dp.message(F.text == "👀 Дивитись анкети")
async def view_profiles(message: Message):
    await show_next_profile(message.from_user.id)

@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    async with aiosqlite.connect("dating.db") as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("DELETE FROM views WHERE viewer_id = ?", (message.from_user.id,))
        await db.commit()
    await message.answer(texts['search_stopped'], reply_markup=get_menu_keyboard())

# Main function to start the bot
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

