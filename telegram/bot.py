
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.web_app_info import WebAppInfo
API_TOKEN = '6025752741:AAFav4ooRRMsHUUHEhvouJznrjjiH2QuzeM'  # Replace with your API token


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Web APp", web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")))
    await message.answer("Привет", reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp)
