from bot import dp, bot
from database.db import db
from database import models
from aiogram.dispatcher import FSMContext
from aiogram import types
from telegram.post import ikbs
from datetime import datetime

@dp.callback_query_handler(lambda с: с.data == "list_of_planned_posts_show")
async def get_list_of_planned_posts(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        curr_page = 0
        data['curr_page'] = curr_page
    
    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
    
    all_planned_posts = db.query(models.Post).filter(models.Post.admin == current_user, models.Post.is_published == False).all()
    if not all_planned_posts:
        await callback_query.answer("К сожалению, нету запланированных постов!")
        return
    

    planned_post = all_planned_posts[curr_page]
    btns = ikbs.get_btns_for_pagination_posts(planned_post, curr_page, all_planned_posts)
    formatted_date = datetime.strftime(planned_post.scheduled_time, "%d %B %Y %H:%M")
    message_text = (
        f"{planned_post.caption}\n\n\n"
        f"Дата публикации:\n"
        f"{formatted_date}"
    )
    if planned_post.photo_dir:
        await callback_query.message.answer_photo(photo=types.InputFile(planned_post.photo_dir), caption=message_text, reply_markup=btns, parse_mode="HTML")
    else:
        await callback_query.message.answer_video(photo=types.InputFile(planned_post.photo_dir), caption=message_text, reply_markup=btns, parse_mode="HTML")
    async with state.proxy() as data:
        data['curr_page'] = curr_page

@dp.callback_query_handler(lambda c: c.data in ["next_post", "prev_post"])
async def pagination_list_planned_posts(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        curr_page = data['curr_page']

    current_user = db.query(models.Admin).filter(models.Admin.tg_id == callback_query.from_user.id).first()
   
    all_planned_posts = db.query(models.Post).filter(models.Post.admin == current_user, models.Post.is_published == False).all()
    if not all_planned_posts:
        # If there are no admins left (except the superuser), inform the user and return
        await callback_query.answer("Больше нет запланированных постов")
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        return
    if callback_query.data == "next_post":
        curr_page += 1
        if curr_page >= len(all_planned_posts):
            await callback_query.answer("Больше нет запланированных постов")
            return
    elif callback_query.data == "prev_post":
        curr_page -= 1
        if curr_page < 0:
            await callback_query.answer("Нет предыдущих")
            return
    planned_post = all_planned_posts[curr_page]
    formatted_date = datetime.strftime(planned_post.scheduled_time, "%d %B %Y %H:%M")
    
    btns = ikbs.get_btns_for_pagination_posts(planned_post, curr_page, all_planned_posts)

    message_text = (
        f"{planned_post.caption}\n\n\n"
        f"Дата публикации:\n"
        f"{formatted_date}"
    )
    if planned_post.photo_dir:
        await callback_query.message.edit_media(media=types.InputMediaPhoto(media=open(planned_post.photo_dir, 'rb'), caption=message_text, parse_mode="HTML"))
        await callback_query.message.edit_reply_markup(reply_markup=btns)
    else:
        await callback_query.message.edit_media(media=types.InputMediaVideo(media=open(planned_post.video_dir, 'rb'), caption=message_text, parse_mode="HTML"))
        await callback_query.message.edit_reply_markup(reply_markup=btns)
    # Get the sent message_id from state and edit the corresponding message
    
    async with state.proxy() as data:
        data['curr_page'] = curr_page

@dp.callback_query_handler(lambda query: query.data.startswith("confirm_delete_planned_post:"))
async def confirm_delete_user_callback(query: types.CallbackQuery):
    planned_post_id = int(query.data.split(':')[-1])
    planned_post = db.query(models.Post).filter(models.Post.id == planned_post_id).first()
    
    del_or_not_btns = ikbs.delete_planned_post(planned_post_id)

    # Send the confirmation message
    formatted_date = datetime.strftime(planned_post.scheduled_time, "%d %B %Y %H:%M")

    message_text = (
        f"{planned_post.caption}\n\n\n"
        f"Дата публикации:\n"
        f"{formatted_date}\n"
        "<b><em>Вы действительно хотите удалить данный пост?</em></b>"
    )
    await query.message.edit_caption(caption=message_text, reply_markup=del_or_not_btns, parse_mode="HTML")

@dp.callback_query_handler(lambda query: query.data.startswith("delete_planned_post_from_list:"))
async def delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    planned_post_id = int(query.data.split(':')[-1])
    planned_post = db.query(models.Post).filter(models.Post.id == planned_post_id).first()
    db.delete(planned_post)
    db.commit()
    await query.answer("ПОСТ БЫЛ УДАЛЕН")
    # Reset the current page to 0 in state.proxy() data
    async with state.proxy() as data:
        data['curr_page'] = 0

    # Call the function to resend the list of admins with the updated page
    await pagination_list_planned_posts(query, state)

@dp.callback_query_handler(lambda query: query.data == "cancel_delete_planned_post")
async def cancel_delete_user_callback(query: types.CallbackQuery, state: FSMContext):
    await query.answer("УДАЛЕНИЕ ОТМЕНЕНО")
    await pagination_list_planned_posts(query, state)

# @dp.callback_query_handler(lambda query: query.data.startswith("cancel_sending_post:"))
# async def cancel_send(query: types.CallbackQuery, state: FSMContext):
#     post_id = int(query.data.split(':')[-1])
#     post = db.query(models.Post).filter(models.Post.id == post_id).first()
#     btns = ikbs.get_btns_for_post(post)
#     if post.photo_dir:
#         await query.message.edit_media(media=types.InputMediaPhoto(media=open(post.photo_dir, 'rb'), caption=post.caption))
#         await query.message.edit_reply_markup(reply_markup=btns)
#     else:
#         await query.message.edit_media(media=types.InputMediaVideo(media=open(post.video_dir, 'rb'), caption=post.caption))
#         await query.message.edit_reply_markup(reply_markup=btns)