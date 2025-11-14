from aiogram.fsm.state import State, StatesGroup


class PriceStates(StatesGroup):
    min_price = State()
    max_price = State()


class ServiceStates(StatesGroup):
    wait_description = State()
    wait_start_address = State()
    wait_end_address = State()