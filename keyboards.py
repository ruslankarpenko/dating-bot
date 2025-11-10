from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup
from texts import texts

def get_greeting_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Ок")
    kb.button(text="У мене вже є анкета")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_create_profile_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Створити")
    return kb.as_markup(resize_keyboard=True)

def get_reply_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="❤️ Вподобати")
    kb.button(text="⏭ Пропустити")
    kb.button(text="📋 Меню")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="✏️ Редагувати анкету")
    kb.button(text="👀 Дивитись анкети")
    kb.button(text="🔄 Редагувати критерії пошуку")
    kb.button(text="❌ Деактивувати анкету")
    return kb.as_markup(resize_keyboard=True)

def get_gender_keyboard_self() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Чоловік")
    kb.button(text="👩 Жінка")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_gender_keyboard_search() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👨 Чоловіка")
    kb.button(text="👩 Жінку")
    kb.button(text="🔹 Обох")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_new_like_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=texts['view_profile'])
    kb.button(text=texts['skip_profile'])
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_skip_bio_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=texts['skip_bio'])
    return kb.as_markup(resize_keyboard=True)

def get_skip_photo_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=texts['skip_photo'])
    return kb.as_markup(resize_keyboard=True)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="📢 Розсилка")
    kb.button(text="🧹 Почистити БД")
    kb.button(text="📋 Показати всі анкети")
    kb.button(text="📊 Отримати БД")
    kb.button(text="🗑 Видалити анкету")
    kb.button(text="🔙 Назад")
    kb.adjust(2, 2, 2)
    return kb.as_markup(resize_keyboard=True)