from bot import bot
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
import asyncio
from database.models import *
from fastapi import APIRouter, Depends, UploadFile, File, status
import shutil
from aiogram import types
import os
from fastapi.staticfiles import StaticFiles
import datetime
from typing import Optional, List
from app.auth.router import router as auth_router
from app.post.router import router as post_router
app = FastAPI(title='TELEGRAM BOT by UTOPIA')
from fastapi.staticfiles import StaticFiles

app.mount('/static', StaticFiles(directory='static'), name='static')

FILEPATH = "./static/files/"  # Define the file path for storing uploaded files
app.include_router(auth_router)
app.include_router(post_router)


# channel_id = -1001610513685
# app.mount('/static', StaticFiles(directory='static'), name='static')

# FILEPATH = "./static/files/"  # Define the file path for storing uploaded files
# ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "video/mp4"]  # List of allowed content types

# from fastapi import Request

# @app.post("/send_post/")
# async def send_message(request: Request, 
#                        background_tasks: BackgroundTasks, 
#                        medias: List[UploadFile] = File(...), 
#                        message: str = Body(None),
#                        date: Optional[str] = Body(None), 
#                        time: Optional[str] = Body(None)):

#     # Convert separate date and time inputs to a single scheduled_datetime
#     scheduled_datetime_str = date + " " + time if date and time else None
#     scheduled_datetime = datetime.datetime.strptime(scheduled_datetime_str, "%Y-%m-%d %H:%M") if scheduled_datetime_str else datetime.datetime.now()

#     # Get the base URL from the request object
#     base_url = request.base_url
    
#     db_post = Post(caption=message, scheduled_time=scheduled_datetime)
#     db.add(db_post)
#     db.commit()

#     for media in medias:
#         if media.content_type not in ALLOWED_CONTENT_TYPES:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid file format. Only photos (JPEG/PNG) and videos (MP4) are allowed.")
#         media_type = "photo" if media.content_type.startswith("image") else "video"

#         filename = media.filename
#         generated_name = os.path.join(FILEPATH, filename)  # Use os.path.join to create the full file path
#         counter = 1
#         while os.path.exists(generated_name):
#             base_name, extension = os.path.splitext(filename)
#             new_filename = f"{base_name}_{counter}{extension}"
#             generated_name = os.path.join(FILEPATH, new_filename)
#             counter += 1
#         file_content = await media.read()
#         with open(generated_name, 'wb') as file:
#             file.write(file_content)

#         # Create the media URLs using the base_url and the generated_name
#         media_url = f'{base_url}{generated_name[2:]}'

#         if media_type == "photo":
#             db_media = Media(post_id=db_post.id, photo_dir=generated_name, photo_url=media_url)  # Save the URL directly for photos
#         else:
#             db_media = Media(post_id=db_post.id, video_dir=generated_name, video_url=media_url)  # Save the file path directly for videos

#         db.add(db_media)
#         db.commit()

#     if len(medias) > 1:
#         db_post.is_media_group = True
#         db.commit()

#     # Schedule the post to be sent in the background
#     background_tasks.add_task(send_post_to_channel, db_post)

#     return {"status": "Message received. Post will be sent at the scheduled time."}

    

# async def send_post_to_channel(post):
#     scheduled_time = post.scheduled_time  

#     time_difference = scheduled_time - datetime.datetime.now()

#     if time_difference.total_seconds() >= 0 or time_difference.total_seconds() < 0:
#         await asyncio.sleep(time_difference.total_seconds())
        
#         if not db.query(Post).filter(Post.id == post.id).first():
#             return

#         if post.is_media_group:
            
#             media_group = []
#             for photo in post.medias:
#                 if photo.photo_url:
#                     media_group.append(types.InputMediaPhoto(types.InputFile(photo.photo_dir)))
#                 else:
#                     media_group.append(types.InputMediaVideo(types.InputFile(photo.video_dir)))
#             media_group[-1].caption = post.caption
            
#             await bot.send_media_group(chat_id=channel_id, media=media_group)

#         else:
#             keyboard = types.InlineKeyboardMarkup()
#             for btn in post.buttons:
#                 keyboard.add(types.InlineKeyboardButton(text=btn.button_name, url=btn.button_url))
           
#             for media in post.medias:
#                 if media.photo_url:  
#                     # Sending photo as a photo message
                    
#                     await bot.send_photo(chat_id=channel_id, photo=types.InputFile(media.photo_dir), caption=post.caption, reply_markup=keyboard, parse_mode="HTML")  
#                 else:
#                     await bot.send_video(chat_id=channel_id, video=types.InputFile(media.video_dir), caption=post.caption, reply_markup=keyboard, parse_mode="HTML")

#         post.is_published = True
#         db.commit()


