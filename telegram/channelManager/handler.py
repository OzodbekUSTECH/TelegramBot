from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types

from aiogram.utils.exceptions import BotBlocked

@dp.callback_query_handler(lambda c: c.data == "invalid_channel_link")
async def warn_invalid_channel_link(callback_query: types.CallbackQuery):
    message_text = (
        "Введите правильное ID канала!"
    )
    await callback_query.answer(text=message_text)


@dp.callback_query_handler(lambda c: c.data == "get_own_subs_statictic")
async def get_own_channel_statistics(callback_query: types.CallbackQuery):
    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
   
    all_subs = db.query(models.User).filter(models.User.admin == current_user).all()

    for sub in all_subs:
        try:
            await bot.send_chat_action(sub.tg_id, action=types.ChatActions.TYPING)
            sub.has_banned = False
        except BotBlocked:
            sub.has_banned = True
        
    db.commit()
    
    banned_subs = db.query(models.User).filter(models.User.has_banned == True, models.User.admin == current_user).all()
    active_subs = db.query(models.User).filter(models.User.has_banned == False, models.User.admin == current_user).all()

    message_text = (
        f"Всего подписчиков:\n"
        f"<b><em>{len(all_subs)}</em></b>\n\n"
        f"Не забанили бота: {len(active_subs)} 🎉\n"
        f"Забанили бота: {len(banned_subs)} 😔"
    )
    kb = types.InlineKeyboardMarkup()
    back_to_menu = types.InlineKeyboardButton("Назад", callback_data="back_to_main_menu")
    kb.add(back_to_menu)
    await callback_query.message.edit_text(text=message_text, reply_markup=kb, parse_mode="HTML")




from telegram.channelManager.paginationbtns import *
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
        
        btns = await get_list_of_all_channels_statistics(curr_page=curr_page, all_channels=all_channels)
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
        active_subs_of_channel = db.query(models.User).filter(models.User.has_banned == False, models.User.admin == channel).all()
        banned_subs_of_channel = db.query(models.User).filter(models.User.has_banned == True, models.User.admin == channel).all()
        btns = await get_list_of_all_channels_statistics(curr_page=curr_page, all_channels=all_channels, channel=channel)

        message_text = (
            f"Админ канала: @{channel.username}\n"
            f"Всего подписчиков:<b><em>{len(channel.users)}</em></b>\n\n"
            f"Не забанили бота: {len(active_subs_of_channel)} 🎉\n"
            f"Забанили бота: {len(banned_subs_of_channel)} 😔"
        )

        await callback_query.message.edit_text(text=message_text, reply_markup=btns, parse_mode="HTML")

        async with state.proxy() as data:
            data['curr_page'] = curr_page