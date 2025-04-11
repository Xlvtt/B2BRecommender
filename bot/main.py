import os
import time

import aiogram.exceptions
import numpy as np
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
                [KeyboardButton(text="Зарегистрироваться")],
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
            samples = ", ".join([str(buyer_id) for buyer_id in data_loader.buyers["PERSON_ID"].sample(n=10, random_state=int(time.time())).values])
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


async def show_main_menu_no_photo(message: types.Message, buyer_id: int, text: str):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Моя компания", callback_data=f"company_{buyer_id}")],
        [InlineKeyboardButton(text="Рекомендации", callback_data=f"recs_{buyer_id}")],
        [InlineKeyboardButton(text="Выход", callback_data="exit")]
    ])
    await message.answer(
        text=text,
        reply_markup=markup
    )


def get_dumped_lots(lots_info: pd.DataFrame) -> str:
    lots_messages = []
    for i, lot in lots_info.iterrows():
        lot_message = f"{i + 1}. ЛОТ {lot["LOT_ID"]}\n"\
            f"\t- Закупка: {lot["LOT_NAME"]}\n"\
            f"\t- Начальная цена: {lot["TOTAL_START_PRICE_RUBLES"]}\n"
        lots_messages.append(lot_message)
    return '\n'.join(lots_messages)


def get_formatted_person_info(person_info: dict, message_path: str) -> str:
    with open(message_path, encoding="utf-8") as message_file:
        message_text = "".join(message_file.readlines())
        for key, value in person_info.items():
            message_text = message_text.replace("{" + key + "}", str(value))
    return message_text


@dp.callback_query(F.data.startswith("company_"))
async def company_info(callback: types.CallbackQuery):
    buyer_id = int(callback.data.split("_")[1])
    buyer_info = data_loader.get_buyer_info(buyer_id)

    buyer_info["id"] = buyer_id
    if len(buyer_info["lots_info"]) == 0:
        buyer_info["lots_info"] = "Вы еще не выставляли ни одного лота :("
    else:
        buyer_info["lots_info"] = get_dumped_lots(buyer_info["lots_info"])

    if buyer_info["favourite_seller_info"] is None:
        buyer_info["favourite_seller_info"] = "Вы еще не взаимодействовали с поставщиками :("

    for key in ["max_start_price", "min_start_price", "max_end_price", "min_end_price"]:
        if np.isnan(buyer_info[key]):
            buyer_info[key] = "?"

    message_text = get_formatted_person_info(buyer_info, "messages/buyers.txt")

    await show_main_menu_no_photo(callback.message, buyer_id, message_text)


@dp.callback_query(F.data.startswith("recs_"))
async def get_recommendations(callback: types.CallbackQuery, state: FSMContext):
    buyer_id = int(callback.data.split("_")[1])

    recommended_sellers = recommender.recommend(buyer_id, k=10).values
    await state.update_data(recommended_sellers=recommended_sellers)

    inline_keyboard = [
        [InlineKeyboardButton(text=f"Поставщик {seller_id}", callback_data=f"seller_{seller_id}_{buyer_id}")]
        for seller_id in recommended_sellers
    ]
    inline_keyboard.append([InlineKeyboardButton(text="В меню", callback_data=f"go_back_{buyer_id}")])
    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await callback.message.answer(
        text=f"Ваши рекомендации готовы!\nВыберите поставщика для подробной информации:",
        reply_markup=markup
    )


@dp.callback_query(F.data.startswith("seller_"))
async def get_seller_info(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    seller_id = int(data[1])
    buyer_id = int(data[2])

    recommended_sellers = (await state.get_value("recommended_sellers")).tolist()

    inline_keyboard = [
        [InlineKeyboardButton(text=f"Поставщик {seller_id}", callback_data=f"seller_{seller_id}_{buyer_id}")]
        for seller_id in recommended_sellers
    ]
    inline_keyboard.append([InlineKeyboardButton(text="В меню", callback_data=f"go_back_{buyer_id}")])

    markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    seller_info = data_loader.get_seller_info(seller_id)

    seller_info["lots_info"] = get_dumped_lots(seller_info["lots_info"])
    seller_info["id"] = seller_id

    message_text = get_formatted_person_info(seller_info, "messages/sellers.txt")

    await callback.message.answer(
        text=message_text,
        reply_markup=markup
    )


@dp.callback_query(F.data.startswith("go_back"))
async def go_back(callback: types.CallbackQuery):
    buyer_id = int(callback.data.split("_")[-1])
    await show_main_menu(callback.message, buyer_id)


@dp.callback_query(F.data == "exit")
async def exit_handler(callback: types.CallbackQuery):
    await start_handler(callback.message)


if __name__ == "__main__":
    dp.run_polling(bot)
