from aiogram.fsm.state import State, StatesGroup


class LanguageStates(StatesGroup):
    choosing = State()
