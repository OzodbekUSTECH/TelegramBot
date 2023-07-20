from telegram.channelManager.paginationbtns import get_channel_link, get_list_of_all_channels_statistics
from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types
from pyrogram import Client

from aiogram.utils.exceptions import BotBlocked

async def get_channel_subscribers(admin_channel_id):
    # Создаем клиент Pyrogram
    api_id = '20122546'
    api_hash = 'c3ca5ae4e368b18eccd06a5edcd7eec0'
    bot_token = '6095169791:AAEQM5y8u1IPLPMhvOZDVQlqTDSMAadjmL0'

    client = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
    
    # Запускаем клиент
    await client.start()
    admin_of_channel = db.query(models.Admin).filter(models.Admin.channel_id == admin_channel_id).first()
    super_admin = db.query(models.Admin).filter(models.Admin.is_superuser == True).first()
    amount_subs = await bot.get_chat_members_count(admin_channel_id)
    all_subs = client.get_chat_members(admin_channel_id)
    if amount_subs != len(admin_of_channel.users):
        async for subscriber in all_subs:
            db_user = db.query(models.User).filter(models.User.tg_id == subscriber.user.id).first()
            if subscriber.user.is_bot == False and not db_user and subscriber.user.id != admin_of_channel.tg_id and subscriber.user.id != super_admin.tg_id:
                
                new_user = models.User(
                    tg_id=subscriber.user.id, 
                    name=subscriber.user.first_name, 
                    admin=admin_of_channel)
                db.add(new_user)
                db.commit()


    all_subs = db.query(models.User).filter(models.User.admin == admin_of_channel).all()

    for sub in all_subs:
        
        try:
            await bot.send_chat_action(sub.tg_id, action=types.ChatActions.TYPING)
            sub.has_banned = False
        except BotBlocked:
            sub.has_banned = True
        
    db.commit()
    await client.stop()






GETIDSBOT_INSTRUCTION = """
- <u>Чтобы получить ID своего аккаунта:</u>
напишите любое сообщение боту @getidsbot.

- <u>Чтобы получить ID телеграм канала</u>
перешлите из своего канала сообщение боту @getidsbot."""
@dp.callback_query_handler(lambda c: c.data == "get_own_subs_statictic")
async def get_own_channel_statistics(callback_query: types.CallbackQuery):
    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
    await callback_query.answer("Обновляем, подождите немного...")
    await get_channel_subscribers(current_user.channel_id)
    all_subs = db.query(models.User).filter(models.User.admin == current_user).all()

    
    
    banned_subs = db.query(models.User).filter(models.User.has_banned == True, models.User.admin == current_user).all()
    active_subs = db.query(models.User).filter(models.User.has_banned == False, models.User.admin == current_user).all()

    
    kb = types.InlineKeyboardMarkup()
    back_to_menu = types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu")
    link = await get_channel_link(current_user.channel_id)
    kb.add(back_to_menu)
    if link is None:
        message_text = (
            "Не получается получить данные канала...\n"
            "*Введите правильное ID канала*\n\n"
            f"*Добавьте бота в канала и дайте ему все права администратора!\n\n"
            "Это можно сделать через <a href='https://t.me/getidsbot'>@getidsbot</a>\n\n"
            "<b>ИНСТРУКЦИЯ:</b>\n"
            f"{GETIDSBOT_INSTRUCTION}"
        )

    else:
        
        message_text = (
            f"Cтатистика моего канала:\n\n"
            
            f"Всего подписчиков: <b><em>{len(all_subs)}</em></b>\n\n"
            f"Не забанили бота: {len(active_subs)} 🎉\n"
            f"Забанили бота: {len(banned_subs)} 😔\n\n"
            f"<a href='{link}'>Перейти в канал</a>"
        )
    await callback_query.message.edit_text(text=message_text, reply_markup=kb, parse_mode="HTML")




