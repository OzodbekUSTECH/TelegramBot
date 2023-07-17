from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types



@dp.message_handler(lambda message: message.text == "Список Админов")
async def get_list_of_admins(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        curr_page = 0
        data['curr_page'] = curr_page
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    current_superuser = db.query(models.Admin).filter(models.Admin.tg_id == message.from_user.id).first()
    if current_superuser:
        all_admins = db.query(models.Admin).filter(models.Admin.id != current_superuser.id).all()
        if not all_admins:
            await bot.send_message(chat_id=message.from_user.id, text="Нет других админов, кроме вас.")
            return
        

      
        admin = all_admins[curr_page]
        
        message_text = (
            f"Админ №: {admin.id}\n"
            f'ID tg: {admin.tg_id}\n'
            f'email: {admin.email}\n'
            f'username: @{admin.username}\n'
            f'Имя: {admin.first_name}\n'
            f'Фамилия: {admin.last_name}\n'
            f'Номер телефона: {admin.phone_number}\n'
            f'ID канала: {admin.channel_id}\n'
        )
        kb = types.InlineKeyboardMarkup()
        closemsg = types.InlineKeyboardButton(text="Скрыть", callback_data="close_msg")
        deletebtn = types.InlineKeyboardButton(text="Удалить", callback_data=f"confirm_delete_admin:{admin.id}")
        backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_post")
        counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 1)}/{str(len(all_admins))}", callback_data='_')
        nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_post")
      
        kb.add(closemsg, deletebtn).add(backbtn, counter_text, nextbtn)

        # Send the message and store the sent message object in state
        sent_message = await bot.send_message(chat_id=message.from_user.id, text=message_text, reply_markup=kb)
        async with state.proxy() as data:
            data['curr_page'] = curr_page
            data['sent_message_id'] = sent_message.message_id


@dp.callback_query_handler(lambda c: c.data in ["next_post", "prev_post"])
async def pagination_list_admin(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        curr_page = data['curr_page']

    current_superuser = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
   
    all_admins = db.query(models.Admin).filter(models.Admin.id != current_superuser.id).all()
      
    if callback_query.data == "next_post":
        curr_page += 1
        if curr_page >= len(all_admins):
            await callback_query.answer("Больше нет Админов")
            return
    elif callback_query.data == "prev_post":
        curr_page -= 1
        if curr_page < 0:
            await callback_query.answer("Нет предыдущих")
            return
    admin = all_admins[curr_page]
    message_text = (
        f"Админ №: {admin.id}\n"
        f'ID tg: {admin.tg_id}\n'
        f'email: {admin.email}\n'
        f'username: @{admin.username}\n'
        f'Имя: {admin.first_name}\n'
        f'Фамилия: {admin.last_name}\n'
        f'Номер телефона: {admin.phone_number}\n'
        f'ID канала: {admin.channel_id}\n'
    )
    kb = types.InlineKeyboardMarkup()
    closemsg = types.InlineKeyboardButton(text="Скрыть", callback_data="close_msg")
    deletebtn = types.InlineKeyboardButton(text="Удалить", callback_data=f"confirm_delete_admin:{admin.id}")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_post")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 1)}/{str(len(all_admins))}", callback_data='_')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_post")

    kb.add(closemsg, deletebtn).add(backbtn, counter_text, nextbtn)
    
    # Get the sent message_id from state and edit the corresponding message
    sent_message_id = data.get('sent_message_id')
    if sent_message_id:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=sent_message_id, text=message_text, reply_markup=kb)

    async with state.proxy() as data:
        data['curr_page'] = curr_page



@dp.callback_query_handler(lambda query: query.data.startswith("confirm_delete_admin:"))
async def confirm_delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    admin_id = int(query.data.split(':')[-1])
    # ... (existing code to get the admin from the database)

    # Create an inline keyboard for the confirmation popup
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"delete_admin_from_list:{admin_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="cancel_delete_admin")
    kb.add(yes_btn, no_btn)

    # Send the confirmation message
   
    await query.message.edit_text("Вы уверены, что хотите удалить администратора?", reply_markup=kb)


@dp.callback_query_handler(lambda query: query.data.startswith("delete_admin_from_list:"))
async def delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    admin_id = int(query.data.split(':')[-1])
    super_user = db.query(models.Admin).filter(models.Admin.is_superuser == True).first()
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if db_admin.users:
        for user in db_admin.users:
            user.admin_id = super_user.id
            db.commit()
    db.delete(db_admin)
    db.commit()
    await query.answer("АДМИН БЫЛ УДАЛЕН")
    # Reset the current page to 0 in state.proxy() data
    async with state.proxy() as data:
        data['curr_page'] = 0

    # Call the function to resend the list of admins with the updated page
    await pagination_list_admin(query, state)


@dp.callback_query_handler(lambda query: query.data == "cancel_delete_admin")
async def cancel_delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    await query.answer("УДАЛЕНИЕ ОТМЕНЕНО")
    await pagination_list_admin(query, state)
