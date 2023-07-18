from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types
from telegram.post import ikbs
import datetime
import asyncio
from telegram.post import ikbs
@dp.callback_query_handler(lambda query: query.data.startswith("cancel_sending_post:"))
async def cancel_send_post(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    btns = ikbs.get_btns_for_post(post)
    formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
    message_text = (
        f'{post.caption}\n\n\n'
        f"<b><em>Дата отправки:</em></b>\n"
        f"{formatted_date}"
    )
    await query.message.edit_caption(caption=message_text, reply_markup=btns, parse_mode="HTML")


#отправить в канал
@dp.callback_query_handler(lambda query: query.data.startswith("confirm_send_to_chanel:"))
async def confirm_send_to_channel(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"send_to_channel:{post_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data=f"cancel_sending_post:{post_id}")
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
    if post.button_name:
        kb.add(post_btn).add(yes_btn, no_btn)
    else:
        kb.add(yes_btn, no_btn)
    message_text = (
        f'{post.caption}\n\n\n'
        f"<b><em>Дата отправки:</em></b>\n"
        f"{formatted_date}\n"
        "<b><em>Вы действитетльно хотите отправить пост в канал?</em></b>"
    )
    
    await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")



@dp.callback_query_handler(lambda query: query.data.startswith("send_to_channel:"))
async def send_to_channel(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post.send_type = "Отправить в канал"
    db.commit()
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    btn_of_post = ikbs.get_post_button(post)
    
    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    closemsg = types.InlineKeyboardButton("Скрыть", callback_data="close_msg")
    if post.button_name:
        kb.add(post_btn).add(closemsg)
    else:
        kb.add(closemsg)
    if time_difference.total_seconds() >= 0:
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост будет отправлен:</em></b>\n"
            f"{formatted_date}"
        )
        
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        await asyncio.sleep(time_difference.total_seconds())
        if post.button_name:
            btn_of_post = ikbs.get_post_button(post)
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post)
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post)
        else:
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption)
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption)
        post.is_published = True
        db.commit()

    else:

        # Форматирование объекта datetime в нужный формат
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост отправлен в канал</em></b>"
        )
    
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        
        if post.button_name:
            
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
        else:
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
        post.is_published = True
        db.commit()


#отправить подписчикам
@dp.callback_query_handler(lambda query: query.data.startswith("confirm_send_to_subs:"))
async def confirm_send_to_subs(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"send_to_subs:{post_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data=f"cancel_sending_post:{post_id}")
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
    if post.button_name:
        kb.add(post_btn).add(yes_btn, no_btn)
    else:
        kb.add(yes_btn, no_btn)
    message_text = (
        f'{post.caption}\n\n\n'
        f"<b><em>Дата отправки:</em></b>\n"
        f"{formatted_date}\n"
        "<b><em>Вы действитетльно хотите отправить пост подписчикам?</em></b>"
    )
    
    await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")



@dp.callback_query_handler(lambda query: query.data.startswith("send_to_subs:"))
async def send_to_subs(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post.send_type = "Отправить подписчикам"
    db.commit()
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    btn_of_post = ikbs.get_post_button(post)

    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    closemsg = types.InlineKeyboardButton("Скрыть", callback_data="close_msg")
    if post.button_name:
        kb.add(post_btn).add(closemsg)
    else:
        kb.add(closemsg)
    if time_difference.total_seconds() >= 0:
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост будет отправлен:</em></b>\n"
            f"{formatted_date}"
        )
        
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        await asyncio.sleep(time_difference.total_seconds())
        
        for user in post.admin.users:
            if post.button_name:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
            
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
                
        post.is_published = True
        db.commit()

    else:

        # Форматирование объекта datetime в нужный формат
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост отправлен подписчикам</em></b>"
        )
    
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        for user in post.admin.users:
            if post.button_name:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
            
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
                
        post.is_published = True
        db.commit()





#отправить подписчикам и в канал
@dp.callback_query_handler(lambda query: query.data.startswith("confirm_send_to_everywhere:"))
async def confirm_send_to_everywhere(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"send_to_everywhere:{post_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data=f"cancel_sending_post:{post_id}")
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
    if post.button_name:
        kb.add(post_btn).add(yes_btn, no_btn)
    else:
        kb.add(yes_btn, no_btn)
    message_text = (
        f'{post.caption}\n\n\n'
        f"<b><em>Дата отправки:</em></b>\n"
        f"{formatted_date}\n"
        "<b><em>Вы действитетльно хотите отправить пост подписчикам и в канал?</em></b>"
    )
    
    await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")



@dp.callback_query_handler(lambda query: query.data.startswith("send_to_everywhere:"))
async def send_to_everywhere(query: types.CallbackQuery):
    post_id = int(query.data.split(':')[-1])
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post.send_type = "Отправить подписчикам и в канал"
    db.commit()
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    btn_of_post = ikbs.get_post_button(post)

    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    closemsg = types.InlineKeyboardButton("Скрыть", callback_data="close_msg")
    if post.button_name:
        kb.add(post_btn).add(closemsg)
    else:
        kb.add(closemsg)
    if time_difference.total_seconds() >= 0:
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост будет отправлен:</em></b>\n"
            f"{formatted_date}"
        )
        
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        await asyncio.sleep(time_difference.total_seconds())
        
        if post.photo_dir:
            await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
        else:
            await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
        post.is_published = True
        db.commit()

    else:

        # Форматирование объекта datetime в нужный формат
        formatted_date = datetime.datetime.strftime(post.scheduled_time, "%d %B %Y %H:%M")
        message_text = (
            f'{post.caption}\n\n\n'
            "<b><em>Пост отправлен подписчикам и в канал</em></b>"
        )
    
        await query.message.edit_caption(caption=message_text, reply_markup=kb, parse_mode="HTML")
        for user in post.admin.users():
            if post.button_name:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
        
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
        if post.button_name:
            if post.button_name:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=btn_of_post, parse_mode="HTML")
            
        else:
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
            
        post.is_published = True
        db.commit()




