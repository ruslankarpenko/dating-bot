from aiogram import F, types
from aiogram.fsm.context import FSMContext

from database import save_user_profile, get_user_view_count, reset_user_view_count
from keyboards import get_gender_keyboard_self, get_gender_keyboard_search, get_skip_bio_keyboard, get_skip_photo_keyboard
from texts import texts
from states import ProfileStates

async def process_name(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Ім'я занадто довге (макс. 50 символів)")
        return
    await state.update_data(name=message.text)
    await message.answer(texts['age'])
    await state.set_state(ProfileStates.age)

async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 16 or age > 100:
            await message.answer("Будь ласка, введіть допустимий вік (16-100)")
            return
        await state.update_data(age=age)
        await message.answer(texts['city'])
        await state.set_state(ProfileStates.city)
    except ValueError:
        await message.answer("Будь ласка, введіть число для віку")

async def process_city(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.answer("Назва міста занадто довга (макс. 50 символів)")
        return
    await state.update_data(city=message.text)
    await message.answer(texts['gender'], reply_markup=get_gender_keyboard_self())
    await state.set_state(ProfileStates.gender)

async def process_gender(message: types.Message, state: FSMContext):
    gender = "Чоловік" if message.text == "👨 Чоловік" else "Жінка"
    await state.update_data(gender=gender)
    await message.answer(texts['bio'], reply_markup=get_skip_bio_keyboard())
    await state.set_state(ProfileStates.bio)

async def wrong_gender(message: types.Message):
    await message.answer("Будь ласка, виберіть стать з клавіатури", reply_markup=get_gender_keyboard_self())

async def process_bio(message: types.Message, state: FSMContext):
    if message.text == texts['skip_bio']:
        bio = texts['default_bio']
    else:
        if len(message.text) > 500:
            await message.answer("Біо занадто довге (макс. 500 символів)")
            return
        bio = message.text

    await state.update_data(bio=bio)
    await message.answer(texts['photo'], reply_markup=get_skip_photo_keyboard())
    await state.set_state(ProfileStates.photo)

async def process_photo(message: types.Message, state: FSMContext):
    if message.text == texts['skip_photo']:
        await state.update_data(photo_id=None)
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    else:
        await message.answer("Будь ласка, надішліть фото або натисніть 'Пропустити фото'")
        return

    data = await state.get_data()
    await save_user_profile(message.from_user.id, data, message.from_user.username)
    
    # Скидаємо лічильник переглядів при створенні профілю
    await reset_user_view_count(message.from_user.id)
    
    await message.answer(texts['search_gender'], reply_markup=get_gender_keyboard_search())
    await state.set_state(ProfileStates.search_gender)