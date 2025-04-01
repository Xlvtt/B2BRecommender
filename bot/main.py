import os
import time

import pandas as pd
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from dotenv import load_dotenv
from pathlib import Path
from loader import DataLoader
from recommender import Recommender

# Инициализация бота
load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

data_loader = DataLoader(data_path=Path(os.getenv("DATA_PATH")))

recommender = Recommender(data_loader)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Form(StatesGroup):
    LOGIN = State()
    REGISTER_ID = State()
    REGISTER_CITY = State()


selected_buyer_id = None


@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    await message.answer_photo(
        types.FSInputFile("images/main.jpeg"),
        caption="Добро пожаловать в систему рекомендаций поставщиков!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Войти по ID")],
                [KeyboardButton(text="Зарегистрироваться")]
            ],
            resize_keyboard=True
        )
    )


@dp.message(F.text == "Войти по ID")
async def login_handler(message: types.Message, state: FSMContext):
    await state.set_state(Form.LOGIN)
    await message.answer("Введите ваш ID заказчика:")


@dp.message(F.text == "Зарегистрироваться")
async def register_handler(message: types.Message, state: FSMContext):
    await state.set_state(Form.REGISTER_ID)
    await message.answer("Введите новый ID заказчика:")


@dp.message(StateFilter(Form.REGISTER_ID))
async def process_register(message: types.Message, state: FSMContext):
    try:
        buyer_id = int(message.text)
        if buyer_id not in data_loader.buyers["PERSON_ID"].values:
            await state.set_state(Form.REGISTER_CITY)
            await state.update_data(buyer_id=buyer_id)
            regions = ", ".join(data_loader.regions[:10].index)
            global selected_buyer_id
            await message.answer(f"Введите регион.\nСамые популярные регионы:\n {regions}")
        else:
            max_id = data_loader.buyers["PERSON_ID"].max()
            await message.answer(f"Такой ID уже существует. Попробуйте еще раз.\nНапример, введите ID больше максимального {max_id}")
    except ValueError:
        await message.answer("Неверный формат ID. Введите число:")


@dp.message(StateFilter(Form.REGISTER_CITY))
async def process_register_city(message: types.Message, state: FSMContext):
    city = message.text
    # No city validation
    buyer_id = await state.get_value("buyer_id")
    data_loader.add_buyer(buyer_id, city)
    await state.clear()
    await show_main_menu(message, buyer_id)


@dp.message(StateFilter(Form.LOGIN))
async def process_login(message: types.Message, state: FSMContext):
    try:
        buyer_id = int(message.text)
        if buyer_id in data_loader.buyers["PERSON_ID"].values:
            await state.clear()
            await show_main_menu(message, buyer_id)
        else:
            samples = ", ".join([str(id) for id in data_loader.buyers["PERSON_ID"].sample(n=10, random_state=int(time.time())).values])
            await message.answer(f"ID не найден. Попробуйте еще раз.\nНапример, выберите один из доступных:\n{samples}")
    except ValueError:
        await message.answer("Неверный формат ID. Введите число:")


async def show_main_menu(message: types.Message, buyer_id: int):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Моя компания", callback_data=f"company_{buyer_id}")],
        [InlineKeyboardButton(text="Рекомендации", callback_data=f"recs_{buyer_id}")],
        [InlineKeyboardButton(text="Выход", callback_data="exit")]
    ])
    await message.answer_photo(
        types.FSInputFile("images/login.png"),
        caption=f"Вы вошли под ID {buyer_id}!\nВыберите действие:",
        reply_markup=markup
    )


@dp.callback_query(F.data.startswith("company_"))
async def company_info(callback: types.CallbackQuery):
    buyer_id = int(callback.data.split("_")[1])
    # TODO Логика отображения информации о компании
    await callback.message.answer(f"Информация о компании {buyer_id}...")


@dp.callback_query(F.data.startswith("recs_"))
async def get_recommendations(callback: types.CallbackQuery):
    buyer_id = int(callback.data.split("_")[1])
    recs = ", ".join([str(id) for id in recommender.recommend(buyer_id, k=10).values])
    await callback.message.answer(f"ID рекомендованных поставщиков:\n{recs}")


@dp.callback_query(F.data == "exit")
async def exit_handler(callback: types.CallbackQuery):
    await start_handler(callback.message)


if __name__ == "__main__":
    dp.run_polling(bot)
