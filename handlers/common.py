import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from database import connect_db

async def show_next_profile(user_id: int):
    db = await connect_db()

    try:
        # Перевіряємо чи користувач має профіль
        async with db.execute(
            "SELECT 1 FROM users WHERE user_id = ?",
            (user_id,)
        ) as cur:
            has_profile = await cur.fetchone()

        if not has_profile:
            await Bot.get_current().send_message(user_id, "Спочатку створіть профіль")
            return

        # Отримуємо дані поточного користувача
        async with db.execute(
            "SELECT gender, city, search_gender, search_age_min, search_age_max FROM users WHERE user_id = ?",
            (user_id,)
        ) as cur:
            user_data = await cur.fetchone()

        if not user_data:
            await Bot.get_current().send_message(user_id, "Спочатку створіть профіль")
            return

        current_gender, city, search_gender, age_min, age_max = user_data

        # Логіка пошуку анкет (як у вашому оригінальному коді)
        if current_gender == "Чоловік":
            if search_gender == "👨 Чоловіка":
                gender_condition = "(gender = 'Чоловік' AND (search_gender = '👨 Чоловіка' OR search_gender = '🔹 Обох'))"
            elif search_gender == "👩 Жінку":
                gender_condition = "(gender = 'Жінка' AND (search_gender = '👨 Чоловіка' OR search_gender = '🔹 Обох'))"
            else:
                gender_condition = "((gender = 'Чоловік' AND (search_gender = '👨 Чоловіка' OR search_gender = '🔹 Обох')) OR (gender = 'Жінка' AND (search_gender = '👨 Чоловіка' OR search_gender = '🔹 Обох')))"
        else:
            if search_gender == "👩 Жінку":
                gender_condition = "(gender = 'Жінка' AND (search_gender = '👩 Жінку' OR search_gender = '🔹 Обох'))"
            elif search_gender == "👨 Чоловіка":
                gender_condition = "(gender = 'Чоловік' AND (search_gender = '👩 Жінку' OR search_gender = '🔹 Обох'))"
            else:
                gender_condition = "((gender = 'Чоловік' AND (search_gender = '👩 Жінку' OR search_gender = '🔹 Обох')) OR (gender = 'Жінка' AND (search_gender = '👩 Жінку' OR search_gender = '🔹 Обох')))"

        # Пошук анкет (як у оригінальному коді)
        same_city_query = f"""
        SELECT user_id, name, age, city, gender, bio, photo_id, username 
        FROM users
        WHERE user_id != ? 
        AND user_id NOT IN (SELECT viewed_id FROM views WHERE viewer_id = ?)
        AND {gender_condition}
        AND age BETWEEN ? AND ?
        AND city LIKE ?
        ORDER BY RANDOM()
        LIMIT 1
        """

        same_city_params = (user_id, user_id, age_min, age_max, f"%{city}%")

        async with db.execute(same_city_query, same_city_params) as cur:
            row = await cur.fetchone()

        if not row:
            other_cities_query = f"""
            SELECT user_id, name, age, city, gender, bio, photo_id, username 
            FROM users
            WHERE user_id != ? 
            AND user_id NOT IN (SELECT viewed_id FROM views WHERE viewer_id = ?)
            AND {gender_condition}
            AND age BETWEEN ? AND ?
            AND city NOT LIKE ?
            ORDER BY RANDOM()
            LIMIT 1
            """

            other_cities_params = (user_id, user_id, age_min, age_max, f"%{city}%")

            async with db.execute(other_cities_query, other_cities_params) as cur:
                row = await cur.fetchone()

        if not row:
            await Bot.get_current().send_message(
                user_id,
                "Немає нових анкет за вашими критеріями. Спробуйте змінити параметри пошуку.",
                reply_markup=get_menu_keyboard()
            )
            return

        uid, name, age, city, gender, bio, photo_id, username = row
        text_parts = [f"*{name}*, {age}", city]
        if bio and bio != texts['default_bio']:
            text_parts.append(bio)
        text = "\n".join(text_parts)

        if photo_id and isinstance(photo_id, str) and len(photo_id) > 10:
            try:
                await Bot.get_current().send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=text,
                    reply_markup=get_reply_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке фото: {str(e)}")
                await Bot.get_current().send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=get_reply_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                await db.execute(
                    "UPDATE users SET photo_id = NULL WHERE user_id = ?",
                    (uid,)
                )
                await db.commit()
        else:
            await Bot.get_current().send_message(
                chat_id=user_id,
                text=text,
                reply_markup=get_reply_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )

        await db.execute("INSERT OR IGNORE INTO views VALUES (?, ?)", (user_id, uid))
        await db.commit()

    except Exception as e:
        logging.error(f"Ошибка в show_next_profile: {str(e)}")
        await Bot.get_current().send_message(
            user_id,
            "⚠️ Произошла ошибка при поиске анкет. Пожалуйста, попробуйте позже.",
            reply_markup=get_menu_keyboard()
        )
    finally:
        await db.close()