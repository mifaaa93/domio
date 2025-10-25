from aiogram.fsm.state import State, StatesGroup


class PriceStates(StatesGroup):
    min_price = State()
    max_price = State()
