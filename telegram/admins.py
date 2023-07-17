from bot import dp, bot
from database.db import db
from database import models

from aiogram import types

@dp.callback_query_handler(lambda query: query.data.startswith("delete_admin:"))
async def delete_user_callback(query: types.CallbackQuery):
    admin_id = int(query.data.split(':')[-1])
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    db.delete(db_admin)
    db.commit()
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text='Админ удален!'
    )

@dp.callback_query_handler(lambda query: query.data.startswith("close_msg"))
async def delete_user_callback(query: types.CallbackQuery):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
