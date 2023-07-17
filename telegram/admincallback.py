from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from telegram.superuser import handler
from aiogram import types
from datetime import datetime


@dp.callback_query_handler(lambda query: query.data.startswith("delete_created_admin:"))
async def confirm_delete_user_callback(query: types.CallbackQuery):
    admin_id = int(query.data.split(':')[-1])

    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"delete_admin:{admin_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data=f"cancel_delete_created_admin:{admin_id}")
    kb.add(yes_btn, no_btn)

    await query.message.edit_text("Вы уверены, что хотите удалить администратора?", reply_markup=kb)

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



@dp.callback_query_handler(lambda query: query.data.startswith("cancel_delete_created_admin:"))
async def cancel_delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    await query.answer("УДАЛЕНИЕ ОТМЕНЕНО")
    admin_id = int(query.data.split(':')[-1])
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not isinstance(db_admin.created_at, datetime):
        db_admin.created_at = datetime.fromisoformat(db_admin.created_at)

    # Форматирование объекта datetime в нужный формат
    formatted_date = db_admin.created_at.strftime("%d %B %Y %H:%M")
    message_text = (
        "Добавлен новый Админ\n\n"
        f'Номер Админа: {db_admin.id}\n'
        f'ID tg: {db_admin.tg_id}\n'
        f'email: {db_admin.email}\n'
        f'username: @{db_admin.username}\n'
        f'Имя: {db_admin.first_name}\n'
        f'Фамилия: {db_admin.last_name}\n'
        f'Номер телефона: {db_admin.phone_number}\n'
        f'ID канала: {db_admin.channel_id}\n'
        f"Дата создания: {formatted_date}"
    )
    buttons_new_admin = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_created_admin:{db_admin.id}")
    close_msg_button = types.InlineKeyboardButton("Скрыть", callback_data=f"close_msg")
    buttons_new_admin.add(delete_button).add(close_msg_button)
    await query.message.edit_text(text=message_text, reply_markup=buttons_new_admin)