from aiogram import F, types
from aiogram.fsm.context import FSMContext
import logging

from database import connect_db, update_user_view_count, get_user_view_count
from keyboards import get_reply_keyboard, get_menu_keyboard, get_gender_keyboard_search
from texts import texts
from states import ProfileStates
from .common import show_next_profile

async def process_search_gender(message: types.Message, state: FSMContext):
    search_gender = message.text
    await state.update_data(search_gender=search_gender)
    await message.answer(texts['search_age_min'])
    await state.set_state(ProfileStates.search_age_min)

async def wrong_search_gender(message: types.Message):
    await message.answer("Будь ласка, виберіть стать з клавіатури", reply_markup=get_gender_keyboard_search())

async def process_search_age_min(message: types.Message, state: FSMContext):
    try:
        age_min = int(message.text)
        if age_min < 16 or age_min > 100:
            await message.answer("Будь ласка, введіть вік від 16 до 100")
            return
        await state.update_data(search_age_min=age_min)
        await message.answer(texts['search_age_max'])
        await state.set_state(ProfileStates.search_age_max)
    except ValueError:
        await message.answer("Будь ласка, введіть число для віку")

async def process_search_age_max(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        age_min = data['search_age_min']
        age_max = int(message.text)

        if age_max < 16 or age_max > 100:
            await message.answer("Будь ласка, введіть вік від 16 до 100")
            return
        if age_max < age_min:
            await message.answer("Максимальний вік не може бути меншим за мінімальний")
            return

        db = await connect_db()
        await db.execute(
            "UPDATE users SET search_gender = ?, search_age_min = ?, search_age_max = ? WHERE user_id = ?",
            (data['search_gender'], age_min, age_max, message.from_user.id)
        )
        await db.commit()
        await db.close()

        await message.answer("❗️Зверніть увагу, що для використання бота у Вас не повинно бути обмежень на пересилання повідомлень\n\nℹ️Інше користувачі, з якими у вас взаємна симпатія, не зможуть Вам написами.\n\n❓Щоб зняти обмеження зміни налаштування приватності в Telegram:\n\n👉 Налаштування → Приватність і безпека → Пересилання повідомлень → Хто може пересилати... → Усі")
        await message.answer(texts['created'], reply_markup=get_reply_keyboard())
        await state.clear()
        await show_next_profile(message.from_user.id)
    except ValueError:
        await message.answer("Будь ласка, введіть число для віку")

async def handle_action(message: types.Message):
    user_id = message.from_user.id

    if message.text == "📋 Меню":
        await message.answer("Оберіть дію:", reply_markup=get_menu_keyboard())
        return

    # Перевіряємо лічильник переглядів
    view_count = await get_user_view_count(user_id)
    if view_count >= 10:
        await message.answer(texts['view_limit_reached'], reply_markup=get_menu_keyboard())
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
            try:
                async with db.execute(
                    "SELECT name, username FROM users WHERE user_id = ?",
                    (to_user,)
                ) as c1:
                    to_name, to_username = await c1.fetchone()
                async with db.execute(
                    "SELECT name, username FROM users WHERE user_id = ?",
                    (user_id,)
                ) as c2:
                    from_name, from_username = await c2.fetchone()

                link1 = f"[{to_name}](tg://user?id={to_user})" + (f" / @{to_username}" if to_username else "")
                link2 = f"[{from_name}](tg://user?id={user_id})" + (f" / @{from_username}" if from_username else "")

                await message.answer(
                    f"{texts['match']} Напишіть одне одному: {link1}",
                    parse_mode="Markdown"
                )
                await message.bot.send_message(
                    to_user,
                    f"{texts['match']} Напишіть одне одному: {link2}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Помилка при надсиланні повідомлення про метчу: {e}")
        else:
            try:
                await message.bot.send_message(
                    to_user,
                    texts['new_like'],
                    reply_markup=get_new_like_keyboard()
                )
                await db.execute(
                    "INSERT OR IGNORE INTO views (viewer_id, viewed_id) VALUES (?, ?)",
                    (to_user, user_id)
                )
            except Exception as e:
                logging.error(f"Помилка при надсиланні повідомлення про лайку: {e}")

        await db.commit()

    # Оновлюємо лічильник переглядів
    new_view_count = await update_user_view_count(user_id)
    await message.answer(texts['view_count'].format(new_view_count))

    await show_next_profile(user_id)