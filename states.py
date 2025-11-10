from aiogram.fsm.state import State, StatesGroup

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

class AdminStates(StatesGroup):
    broadcast_message = State()
    clean_db_amount = State()
    delete_profile_id = State()
    delete_profile_reason = State()