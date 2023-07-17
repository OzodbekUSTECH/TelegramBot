
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.web_app_info import WebAppInfo
from database.db import db
from fastapi import Depends

from database import models
API_TOKEN = '6025752741:AAFav4ooRRMsHUUHEhvouJznrjjiH2QuzeM'  # Replace with your API token


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



@dp.chat_join_request_handler()
async def join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    channel_id = update.chat.id
    admin = db.query(models.Admin).filter(models.Admin.channel_id == channel_id).first()
    user = db.query(models.User).filter(models.User.tg_id == user_id).first()
    if not user:
        user = models.User(
            tg_id=user_id, 
            name=update.from_user.first_name, 
            admin=admin)
        db.add(user)
        db.commit()
    
    # await bot.send_message(user_id, 'Спасибо за подписку!')
    await update.approve()



from telegram.superuser.inlinekeyboards import get_started_buttons
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    db_user = db.query(models.Admin).filter(models.Admin.tg_id == user_id).first()
    if db_user.is_superuser:
        btns = get_started_buttons(db_user)
        await message.answer(f"Привет, {db_user.first_name}", reply_markup=btns)
    elif db_user.is_superuser == False:
        await message.answer(f"Привет, {db_user.first_name}")
    else:
        await message.answer("Здравствуйте, чтобы пользоваться этим ботом,\n"
                             "Напишите Создателю бота!")

from telegram.admincallback import *
from telegram.superuser.handler import *

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)