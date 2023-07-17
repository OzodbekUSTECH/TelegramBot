
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




@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonWebApp(text="VIEW WEB", web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")))
    
    user_id = message.from_user.id
    db_user = db.query(models.Admin).filter(models.Admin.tg_id == user_id).first()

    await message.answer(f"Привет, {db_user.first_name}")


from telegram.admins import *

if __name__ == '__main__':
    executor.start_polling(dp)
