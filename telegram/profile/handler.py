from telegram.channelManager.paginationbtns import get_channel_link, get_list_of_all_channels_statistics
from bot import dp
from database.db import db
from database import models
from aiogram import types
import datetime
from aiogram.types.web_app_info import WebAppInfo




@dp.callback_query_handler(lambda c: c.data.startswith("get_my_info:"))
async def get_own_info(callback_query: types.CallbackQuery):
    admin_id = int(callback_query.data.split(":")[-1])
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        await callback_query.answer("Что-то пошло не так!")
        return
    
    formatted_date = datetime.datetime.strftime(db_admin.created_at, "%d %B %Y %H:%M")
    message_text = (
        f'Ваш номер: {db_admin.id}\n'
        f'ID tg: {db_admin.tg_id}\n'
        f'email: {db_admin.email}\n'
        f'username: @{db_admin.username}\n'
        f'Имя: {db_admin.first_name}\n'
        f'Фамилия: {db_admin.last_name}\n'
        f'Номер телефона: {db_admin.phone_number}\n'
        f'ID канала: {db_admin.channel_id}\n'
        f'Супер Админ: {db_admin.is_superuser}\n'
        f"Дата создания: {formatted_date}"
    )

    btns = get_btns_for_profile(db_admin)
    await callback_query.message.edit_text(message_text, reply_markup=btns)

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME = "naimovozod81@gmail.com",
    MAIL_PASSWORD = "nqddzknaqybrdojn",
    MAIL_FROM = "naimovozod81@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME = "Desired Name",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

import string
import random
from app.auth.utils import pwd_context
def generate_random_password(length):
    alphanumeric = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric) for _ in range(length))

@dp.callback_query_handler(lambda c: c.data.startswith("reset_password:"))
async def get_new_password(callback_query: types.CallbackQuery):
    admin_id = int(callback_query.data.split(":")[-1])
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        await callback_query.answer("Что-то пошло не так!")
        return
    
    new_password = generate_random_password(15)
    hashed_password = pwd_context.hash(new_password)
    db_admin.password = hashed_password
    db.commit()
    
    html = f"Ваш новый пароль: {new_password}"

    message = MessageSchema(
        subject="Восстановление пароля",
        recipients=[db_admin.email],
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    fm.send_message(message)

    await callback_query.message.edit_text("Новый пароль был отправлен на вашу почту!")



def get_btns_for_profile(admin):
    kb = types.InlineKeyboardMarkup()
    reset_password = types.InlineKeyboardButton("Забыл пароль", callback_data=f"reset_password:{admin.id}")
    edit_profile = types.InlineKeyboardButton(text="Редактировать", web_app=WebAppInfo(url="https://vladlenkhan.github.io/tgbot/"))
    backbtn = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    kb.add(edit_profile).add(backbtn).add(reset_password)

    return kb