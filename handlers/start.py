from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from database import get_user_profile, get_user_view_count, reset_user_view_count
from keyboards import get_greeting_keyboard, get_create_profile_keyboard, get_menu_keyboard
from texts import texts
from states import ProfileStates

async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(texts['greeting'], reply_markup=get_greeting_keyboard())

async def start_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(texts['start'])
    await state.set_state(ProfileStates.name)

async def show_existing_profile(message: types.Message):
    user_id = message.from_user.id
    row = await get_user_profile(user_id)

    if row:
        name, age, city, gender, bio, photo_id = row
        text_parts = [f"*{name}*, {age}", city]
        if bio and bio != texts['default_bio']:
            text_parts.append(bio)
        text = "\n".join(text_parts)

        if photo_id:
            await message.answer_photo(
                photo_id,
                caption=text,
                reply_markup=get_menu_keyboard(),
                parse_mode=types.ParseMode.MARKDOWN
            )
        else:
            await message.answer(
                text,
                reply_markup=get_menu_keyboard(),
                parse_mode=types.ParseMode.MARKDOWN
            )
    else:
        await message.answer("У вас немає анкети.", reply_markup=get_create_profile_keyboard())