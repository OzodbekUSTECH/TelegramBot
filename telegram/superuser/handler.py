from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types
from telegram.superuser.inlinekeyboards import get_list_of_all_admin, delete_admin_or_not
from datetime import datetime
from telegram.superuser.inlinekeyboards import get_started_buttons

@dp.callback_query_handler(lambda с: с.data == "list_of_admins_show")
async def get_list_of_admins(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        curr_page = 0
        data['curr_page'] = curr_page
    
    current_superuser = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
    if current_superuser:
        all_admins = db.query(models.Admin).filter(models.Admin.id != current_superuser.id).all()
        if not all_admins:
            await callback_query.answer("К сожалению, нету админов")
            return
        

        admin = all_admins[curr_page]
        if not isinstance(admin.created_at, datetime):
            admin.created_at = datetime.fromisoformat(admin.created_at)

        # Форматирование объекта datetime в нужный формат
        formatted_date = admin.created_at.strftime("%d %B %Y %H:%M")
        message_text = (
            f"Админ №: {admin.id}\n"
            f'ID tg: {admin.tg_id}\n'
            f'email: {admin.email}\n'
            f'username: @{admin.username}\n'
            f'Имя: {admin.first_name}\n'
            f'Фамилия: {admin.last_name}\n'
            f'Номер телефона: {admin.phone_number}\n'
            f'ID канала: {admin.channel_id}\n'
            f'Супер Админ: {admin.is_superuser}\n'
            f'Дата создания: {formatted_date}'
        )
        
        buttons = get_list_of_all_admin(admin, curr_page, all_admins)
        # Send the message and store the sent message object in state
        await callback_query.message.edit_text(text=message_text,reply_markup=buttons)
        async with state.proxy() as data:
            data['curr_page'] = curr_page
           


@dp.callback_query_handler(lambda c: c.data in ["next_admin", "prev_admin"])
async def pagination_list_admin(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        curr_page = data['curr_page']

    current_superuser = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
   
    all_admins = db.query(models.Admin).filter(models.Admin.id != current_superuser.id).all()
    if not all_admins:
        # If there are no admins left (except the superuser), inform the user and return
        await callback_query.answer("Больше нет Админов")
        await back_to_main_menu(callback_query)
        return
    if callback_query.data == "next_admin":
        curr_page += 1
        if curr_page >= len(all_admins):
            await callback_query.answer("Больше нет Админов")
            return
    elif callback_query.data == "prev_admin":
        curr_page -= 1
        if curr_page < 0:
            await callback_query.answer("Нет предыдущих")
            return
    admin = all_admins[curr_page]
    if not isinstance(admin.created_at, datetime):
            admin.created_at = datetime.fromisoformat(admin.created_at)

    # Форматирование объекта datetime в нужный формат
    formatted_date = admin.created_at.strftime("%d %B %Y %H:%M")
    message_text = (
        f"Админ №: {admin.id}\n"
        f'ID tg: {admin.tg_id}\n'
        f'email: {admin.email}\n'
        f'username: @{admin.username}\n'
        f'Имя: {admin.first_name}\n'
        f'Фамилия: {admin.last_name}\n'
        f'Номер телефона: {admin.phone_number}\n'
        f'ID канала: {admin.channel_id}\n'
        f'Супер Админ: {admin.is_superuser}\n'
        f'Дата создания: {formatted_date}'
    )
    buttons = get_list_of_all_admin(admin, curr_page, all_admins)
    await callback_query.message.edit_text(text=message_text, reply_markup=buttons)
    # Get the sent message_id from state and edit the corresponding message
    
    async with state.proxy() as data:
        data['curr_page'] = curr_page




@dp.callback_query_handler(lambda query: query.data.startswith("confirm_delete_admin:"))
async def confirm_delete_user_callback(query: types.CallbackQuery):
    admin_id = int(query.data.split(':')[-1])

    
    del_or_not_btns = delete_admin_or_not(admin_id)

    # Send the confirmation message
   
    await query.message.edit_text("Вы уверены, что хотите удалить администратора?", reply_markup=del_or_not_btns)


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

@dp.callback_query_handler(lambda query: query.data.startswith("back_to_main_menu"))
async def back_to_main_menu(query: types.CallbackQuery):
    user_id = query.from_user.id
    db_user = db.query(models.Admin).filter(models.Admin.tg_id == user_id).first()
    if not db_user:
        await query.message.edit_text(
                            "Здравствуйте, чтобы пользоваться этим ботом,\n"
                             "Напишите Создателю бота!")
    
    btns = get_started_buttons(db_user)

    await query.message.edit_text(f"Привет, {db_user.first_name}", reply_markup=btns)




#КАНАЛЫ
from aiogram.utils.exceptions import BotBlocked, ChatNotFound

from telegram.channelManager.paginationbtns import get_list_of_all_channels_statistics, get_channel_link
@dp.callback_query_handler(lambda c: c.data == "get_all_statistics_of_channels")
async def get_all_channels_statistics(callback_query: types.CallbackQuery, state: FSMContext):
    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
    if current_user.is_superuser:
        async with state.proxy() as data:
            curr_page = -1
            data['curr_page'] = curr_page
        all_subs = db.query(models.User).all()
        
        for sub in all_subs:
            try:
                await bot.send_chat_action(sub.tg_id, action=types.ChatActions.TYPING)
                sub.has_banned = False
            except BotBlocked:
                sub.has_banned = True
            except ChatNotFound:
                # Handle the exception (optional, you can choose to ignore it if you want).
                pass
            
        db.commit()
        
        banned_subs = db.query(models.User).filter(models.User.has_banned == True).all()
        active_subs = db.query(models.User).filter(models.User.has_banned == False).all()
        all_channels = db.query(models.Admin).filter(models.Admin.channel_id != current_user.channel_id).all()
        message_text = (
            f"Всего каналов: {len(all_channels)}\n"
            f"Всего подписчиков:<b><em>{len(all_subs)}</em></b>\n\n"
            
            f"Не забанили бота: {len(active_subs)} 🎉\n"
            f"Забанили бота: {len(banned_subs)} 😔"
        )
        
        btns =  get_list_of_all_channels_statistics(curr_page=curr_page, all_channels=all_channels)
        await callback_query.message.edit_text(text=message_text, reply_markup=btns, parse_mode="HTML")
        async with state.proxy() as data:
            data['curr_page'] = curr_page







@dp.callback_query_handler(lambda c: c.data in ['next_channel', 'prev_channel'])
async def pagination_list_of_channels(callback_query: types.CallbackQuery, state: FSMContext):
    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
    if current_user.is_superuser:
        async with state.proxy() as data:
            curr_page = data['curr_page']

        all_channels = db.query(models.Admin).filter(models.Admin.channel_id != current_user.channel_id).all()
        if not all_channels:
            await callback_query.answer("Нету каналов!")
            return
        
            
        if callback_query.data == "next_channel":
            curr_page += 1
            if curr_page >= len(all_channels):
                await callback_query.answer("Больше нет каналов")
                return
        if callback_query.data == "prev_channel":
            curr_page -= 1
            if curr_page == -1:
                await get_all_channels_statistics(callback_query, state)
                return
            elif curr_page <= -2:
                await callback_query.answer("Вы и так в начальной странице")
                return
        

        channel = all_channels[curr_page]

        enter_channel_link = await get_channel_link(channel.channel_id)
        print(enter_channel_link)
        print(enter_channel_link)
        print(enter_channel_link)
        print(enter_channel_link)
        print(enter_channel_link)

        active_subs_of_channel = db.query(models.User).filter(models.User.has_banned == False, models.User.admin == channel).all()
        banned_subs_of_channel = db.query(models.User).filter(models.User.has_banned == True, models.User.admin == channel).all()
        btns =  get_list_of_all_channels_statistics(curr_page=curr_page, all_channels=all_channels, channel=channel, link_channel=enter_channel_link)

        if enter_channel_link is None:
            message_text = (
                "Не получается получить данные канала...\n\n"
                "Причина: \n"
                "- Введено неправильно ID канала!\n"
                "- Админ не добавил бота в канал!\n"
                "- Не дал доступ администратора боту!\n\n"
                f"Админ канала: @{channel.username}\n"
            )
        else:
            message_text = (
                f"Админ канала: @{channel.username}\n"
                f"Всего подписчиков:<b><em>{len(channel.users)}</em></b>\n\n"
                f"Не забанили бота: {len(active_subs_of_channel)} 🎉\n"
                f"Забанили бота: {len(banned_subs_of_channel)} 😔"
            )

        await callback_query.message.edit_text(text=message_text, reply_markup=btns, parse_mode="HTML")

        async with state.proxy() as data:
            data['curr_page'] = curr_page