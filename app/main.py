from telegram.bot import bot
from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
import asyncio
from database.db import db
from database.models import *
from fastapi import APIRouter, Depends, UploadFile, File, status
import shutil
from aiogram import types
import os
from fastapi.staticfiles import StaticFiles
import datetime
# Replace 'Asia/Tashkent' with your desired timezone

app = FastAPI(title='Minzifa travel api')
channel_id = -1001610513685
app.mount('/static', StaticFiles(directory='static'), name='static')

FILEPATH = "./static/files/"  # Define the file path for storing uploaded files
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "video/mp4"]  # List of allowed content types

@app.post("/send_post/")
async def send_message(background_tasks: BackgroundTasks, media: UploadFile = File(...), message: str = Body(...), time: str = Body(...)):
   
        # scheduled_time = datetime.datetime.fromisoformat(time)

        db_post = Post(caption=message, scheduled_time=time)
        db.add(db_post)
        db.commit()

        if media.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid file format. Only photos (JPEG/PNG) and videos (MP4) are allowed.")

        media_type = "photo" if media.content_type.startswith("image") else "video"

        filename = media.filename
        generated_name = os.path.join(FILEPATH, filename)  # Use os.path.join to create the full file path
        counter = 1
        while os.path.exists(generated_name):
            base_name, extension = os.path.splitext(filename)
            new_filename = f"{base_name}_{counter}{extension}"
            generated_name = os.path.join(FILEPATH, new_filename)
            counter += 1
        file_content = await media.read()
        with open(generated_name, 'wb') as file:
            file.write(file_content)
        
        if media_type == "photo":
            db_media = Media(post_id=db_post.id, photo_url=generated_name)  # Save the file path directly for photos
        else:
            db_media = Media(post_id=db_post.id, video_url=generated_name)  # Save the file path directly for videos
        
        db.add(db_media)
        db.commit()

        # Schedule the post to be sent in the background
        background_tasks.add_task(send_post_to_channel, db_post)

        return {"status": "Message received. Post will be sent at the scheduled time."}
    
    

async def send_post_to_channel(post):
    scheduled_time = post.scheduled_time  

    time_difference = scheduled_time - datetime.datetime.now()
    print(scheduled_time)
    print(datetime.datetime.now())
    print(time_difference)
    print(f"Sending post with ID {post.id} at scheduled time: {scheduled_time}")
    if time_difference.total_seconds() >= 0 or time_difference.total_seconds() < 0:
        await asyncio.sleep(time_difference.total_seconds())
        
        if not db.query(Post).filter(Post.id == post.id).first():
            return
        print("-------------------------------")
        print("-------------------------------")
        print("-------------------------------")
        print("-------------------------------")
        print("-------------------------------")
        if post.is_media_group:
            
            media_group = []
            for photo in post.medias:
                if photo.photo_url:
                    media_group.append(types.InputMediaPhoto(photo.photo_url))
                else:
                    media_group.append(types.InputMediaVideo(photo.video_url))
            media_group[-1].caption = post.caption
            
            await bot.send_media_group(chat_id=channel_id, media=media_group)

        else:
       
            for media in post.medias:
                if media.photo_url:  
                    # Sending photo as a photo message
                    
                    await bot.send_photo(chat_id=channel_id, photo=types.InputFile(media.photo_url), caption=post.caption)  
                else:
                    await bot.send_video(chat_id=channel_id, video=types.InputFile(media.video_url), caption=post.caption)
        print('sended')
        print('sended')
        print('sended')
        print('sended')
        post.is_published = True
        db.commit()
