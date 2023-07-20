from telegram.channelManager.paginationbtns import get_channel_link, get_list_of_all_channels_statistics
from bot import dp
from database.db import db
from database import models
from aiogram import types
import datetime
from aiogram.types.web_app_info import WebAppInfo

def get_btns_for_profile(admin):
    kb = types.ReplyKeyboardMarkup()
    edit_profile = types.InlineKeyboardButton("Редактировать", web_app=WebAppInfo(url="https://vladlenkhan.github.io/tgbot/"))
    backbtn = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    kb.add(edit_profile).add(backbtn)

    return kb


@dp.callback_query_handler(lambda c: c.data.startswith("get_my_info:"))
async def get_own_info(callback_query: types.CallbackQuery):
    admin_id = int(callback_query.data.split(":")[-1])
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        await callback_query.answer("Что-то пошло не так!")
        return
    
    formatted_date = datetime.datetime.strftime(db_admin.created_at, "%d %B %Y %H:%M")
    message_text = (
        f'Ваш: {db_admin.id}\n'
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


