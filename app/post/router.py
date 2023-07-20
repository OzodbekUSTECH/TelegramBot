from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, UploadFile, File, Body
from database.db import get_db
from sqlalchemy.orm import Session
from database import models
from app.auth.utils import get_current_user
import os
from bot import bot
from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from telegram.superuser.inlinekeyboards import get_buttons_for_new_admin
from fastapi import Request
from typing import Optional, List
import datetime
from app.post import utils
from app.post.schema import PostSchema, CreatePostResponseSchema
router = APIRouter(
    prefix='/api/v1',
    tags = ['post']
)

from fastapi.staticfiles import StaticFiles
from telegram.post.ikbs import get_btns_for_post
router.mount('/static', StaticFiles(directory='static'), name='static')

 # Define the file path for storing uploaded files
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "video/mp4"]  # List of allowed content types




@router.get('/post/{post_id}', name="get post by ID", response_model = PostSchema) #добавить сюда curretn user
async def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    raise db_post
@router.post("/post", name='create post', response_model=CreatePostResponseSchema)
async def send_message(request: Request, 
                       background_tasks: BackgroundTasks, 
                       media: UploadFile = File(...), 
                       message: str = Body(''),
                       date: Optional[str] = Body(None), 
                       time: Optional[str] = Body(None),
                       button_name: Optional[str] = Body(None), 
                       button_url: Optional[str] = Body(None), 
                       current_user=Depends(get_current_user), db: Session = Depends(get_db)):

    # Convert separate date and time inputs to a single scheduled_datetime
    if date and time:
        scheduled_datetime_str = date + " " + time
    elif time:
        scheduled_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d") + " " + time
    else:
        scheduled_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    scheduled_datetime = datetime.datetime.strptime(scheduled_datetime_str, "%Y-%m-%d %H:%M")

    # Get the base URL from the request object
    base_url = request.base_url
    
    if media.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid file format. Only photos (JPEG/PNG) and videos (MP4) are allowed.")
    media_type = "photo" if media.content_type.startswith("image") else "video"
    FILEPATH = "./static/files/"
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
    media.close()
    # Create the media URLs using the base_url and the generated_name
    media_url = f'{base_url}{generated_name[2:]}'
    
    if media_type == "photo":
        db_post = models.Post(caption=message, scheduled_time=scheduled_datetime, photo_dir=generated_name, photo_url=media_url, admin=current_user, button_name=button_name, button_url=button_url)  # Save the URL directly for photos
    else:
        db_post = models.Post(caption=message, scheduled_time=scheduled_datetime, video_dir=generated_name, video_url=media_url, admin=current_user,button_name=button_name, button_url=button_url)  # Save the file path directly for videos

    db.add(db_post)
    db.commit()

    

    async def send_message_task():
        
        formatted_date = datetime.datetime.strftime(db_post.scheduled_time, "%d %B %Y %H:%M")
        btns = get_btns_for_post(db_post)
        message_text = (
            f"{db_post.caption}\n\n"
            f"Номер поста: {db_post.id}\n"
            f"<b><em>Дата отправки:</em></b>\n"
            f"{formatted_date}"
        )
        if db_post.photo_url:  
            
            
            await bot.send_photo(chat_id=current_user.tg_id, photo=types.InputFile(db_post.photo_dir), caption=message_text, reply_markup=btns, parse_mode="HTML")  
        else:
            await bot.send_video(chat_id=current_user.tg_id, video=types.InputFile(db_post.video_dir), caption=message_text, reply_markup=btns, parse_mode="HTML")

    background_tasks.add_task(send_message_task)

    response = CreatePostResponseSchema(
        id = db_post.id,
        caption = db_post.caption,
        scheduled_time=db_post.scheduled_time,
        is_published=db_post.is_published,
        photo_dir = db_post.photo_dir,
        photo_url = db_post.photo_url,
        video_dir = db_post.video_dir,
        button_name = db_post.button_name,
        button_url = db_post.button_url,
        admin_id = db_post.admin_id
    )
    return response


@router.put('/post/{post_id}')
async def update_post_data(post_id:int,
                       request: Request, 
                       background_tasks: BackgroundTasks, 
                       media: UploadFile = File(None), 
                       message: Optional[str] = Body(None),
                       date: Optional[str] = Body(None), 
                       time: Optional[str] = Body(None),
                       button_name: Optional[str] = Body(None), 
                       button_url: Optional[str] = Body(None), 
                       current_user=Depends(get_current_user),
                       db: Session = Depends(get_db)):
    
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    previous_datetime = post.scheduled_time
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.admin != current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Its not your post")
    
    if media is not None:
        base_url = request.base_url
    
        if media.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid file format. Only photos (JPEG/PNG) and videos (MP4) are allowed.")
        media_type = "photo" if media.content_type.startswith("image") else "video"
        FILEPATH = "./static/files/"
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
        media.close()
        # Create the media URLs using the base_url and the generated_name
        media_url = f'{base_url}{generated_name[2:]}'

        if media_type == "photo":
            post.photo_dir = generated_name
            post.photo_url = media_url
        else:
            post.video_dir = generated_name
            post.video_url = media_url

    if message is not None:
        post.caption = message
        db.commit()
    if date is not None or time is not None:
        scheduled_datetime = post.scheduled_time if post.scheduled_time else datetime.datetime.now()
        
        if date is not None:
            scheduled_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            scheduled_datetime = scheduled_datetime.combine(scheduled_date, scheduled_datetime.time())
        if time is not None:
            scheduled_time = datetime.datetime.strptime(time, "%H:%M").time()
            scheduled_datetime = scheduled_datetime.combine(scheduled_datetime.date(), scheduled_time)
        post.scheduled_time = scheduled_datetime
        db.commit()
    
    if button_name is not None and button_url is not None:
        post.button_name = button_name
        post.button_url = button_url
        db.commit()
        

    db.commit()
    db.refresh(post)
    if post.scheduled_time != previous_datetime:
        if post.send_type == 'Отправить в канал':
            background_tasks.add_task(utils.send_to_channel, post)

        elif post.send_type == 'Отправить подписчикам':
            background_tasks.add_task(utils.send_to_subs, post)

        elif post.send_type == 'Отправить подписчикам и в канал':
            background_tasks.add_task(utils.send_to_everywhere, post)
   


    return {"message": "UPDATED"}





