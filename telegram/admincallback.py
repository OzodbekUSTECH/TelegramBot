from bot import dp, bot
from database.db import db
from database import models

from aiogram import types

@dp.callback_query_handler(lambda query: query.data.startswith("delete_admin:"))
async def delete_user_callback(query: types.CallbackQuery):
    admin_id = int(query.data.split(':')[-1])
    super_user = db.query(models.Admin).filter(models.Admin.is_superuser == True).first()
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if db_admin.users:
        for user in db_admin.users:
            user.admin_id = super_user.id
            db.commit()
    db.delete(db_admin)
    db.commit()
    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id)
    await query.answer("АДМИН УДАЛЕН")

@dp.callback_query_handler(lambda query: query.data.startswith("close_msg"))
async def delete_user_callback(query: types.CallbackQuery):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)


from telegram.superuser.inlinekeyboards import list_of_admins
@dp.callback_query_handler(lambda query: query.data.startswith("back_to_main_menu"))
async def back_to_main_menu(query: types.CallbackQuery):
    user_id = query.from_user.id
    db_user = db.query(models.Admin).filter(models.Admin.tg_id == user_id).first()
    if db_user.is_superuser:
        await query.message.edit_text(f"Привет, {db_user.first_name}", reply_markup=list_of_admins)
