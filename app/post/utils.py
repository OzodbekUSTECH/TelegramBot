from database.db import db
from database import models
import datetime
from aiogram import types
import asyncio
from bot import bot


#отправить канал после внесения изменений
async def send_to_channel(update_post):
    post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
    
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    
    if post.button_name and post.button_url:
        kb = types.InlineKeyboardMarkup()
        post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
        kb.add(post_btn)
    
    if time_difference.total_seconds() >= 0:
        
        await asyncio.sleep(time_difference.total_seconds()) 
        post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
        db.refresh(post)
        
        if post.scheduled_time <= datetime.datetime.now() and post.is_published == False:
            if post.button_name:
                
                if post.photo_dir:
                    await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
            print("daiwokdawdjoawpdkawod")
            print("daiwokdawdjoawpdkawod")
            print("daiwokdawdjoawpdkawod")
            print("daiwokdawdjoawpdkawod")
            print("daiwokdawdjoawpdkawod")
            post.is_published = True
            db.commit()
            db.refresh(post)
  
    else:

        # Форматирование объекта datetime в нужный формат        
        if post.button_name:
            
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
        else:
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
        post.is_published = True
        db.commit()



#отправить всем подписчикам после изменений
async def send_to_subs(update_post):
    post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
    
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    
    if post.button_name and post.button_url:
        kb = types.InlineKeyboardMarkup()
        post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
        kb.add(post_btn)
    
    if time_difference.total_seconds() >= 0:
        
        await asyncio.sleep(time_difference.total_seconds())
        post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
        db.refresh(post)
        
        if post.scheduled_time <= datetime.datetime.now() and post.is_published == False:
            for user in post.admin.users:
                if post.button_name:
                    
                    if post.photo_dir:
                        await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                    else:
                        await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb)
                else:
                    if post.photo_dir:
                        await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption)
                    else:
                        await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption)

            post.is_published = True
            db.commit()

    else:

        for user in post.admin.users:
            if post.button_name:
                
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb)
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption)
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption)

        post.is_published = True
        db.commit()



#отправить в канал и подписчикам после изменений
async def send_to_everywhere(update_post):
    post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
    
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    
    
    if post.button_name and post.button_url:
        kb = types.InlineKeyboardMarkup()
        post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
        kb.add(post_btn)
    
    if time_difference.total_seconds() >= 0:
        
        await asyncio.sleep(time_difference.total_seconds())
        post = db.query(models.Post).filter(models.Post.id == update_post.id).first()
        db.refresh(post)
        
        if post.scheduled_time <= datetime.datetime.now() and post.is_published == False:
            for user in post.admin.users():
                if post.button_name:
                    if post.photo_dir:
                        await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                    else:
                        await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
            
                else:
                    if post.photo_dir:
                        await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                    else:
                        await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
            if post.button_name:
                if post.button_name:
                    await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
                
            post.is_published = True
            db.commit()

    else:

        for user in post.admin.users():
            if post.button_name:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
        
            else:
                if post.photo_dir:
                    await bot.send_photo(chat_id=user.tg_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
                else:
                    await bot.send_video(chat_id=user.tg_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
        if post.button_name:
            if post.button_name:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, reply_markup=kb, parse_mode="HTML")
            
        else:
            if post.photo_dir:
                await bot.send_photo(chat_id=post.admin.channel_id, photo=types.InputFile(post.photo_dir), caption=post.caption, parse_mode="HTML")
            else:
                await bot.send_video(chat_id=post.admin.channel_id, photo=types.InputFile(post.video_dir), caption=post.caption, parse_mode="HTML")
            
        post.is_published = True
        db.commit()