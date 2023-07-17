from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from database.db import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils import *
from sqlalchemy.exc import IntegrityError
from app.auth.schema import *
from bot import bot
from aiogram import types

router = APIRouter(
    prefix='/api/v1',
    tags = ['Administrator']
)



@router.post('/user', summary="Create a new user", response_model=AdminSchema)
async def register(background_tasks: BackgroundTasks,admin: AdminCreateSchema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа.")

    hashed_password = pwd_context.hash(admin.password)
    db_admin = models.Admin(
        tg_id=admin.tg_id,
        email=admin.email,
        username=admin.username,
        first_name=admin.first_name,
        last_name=admin.last_name,
        phone_number=admin.phone_number,
        channel_id=admin.channel_id,
        is_superuser=admin.is_superuser,
    )
    db_admin.password = hashed_password
    try:
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")

    async def send_message_task():
        if not isinstance(db_admin.created_at, datetime):
            db_admin.created_at = datetime.fromisoformat(db_admin.created_at)

        # Форматирование объекта datetime в нужный формат
        formatted_date = db_admin.created_at.strftime("%d %B %Y %H:%M")
        message_text = (
            "Добавлен новый Админ\n\n"
            f'Номер Админа: {db_admin.id}\n'
            f'ID tg: {db_admin.tg_id}\n'
            f'email: {db_admin.email}\n'
            f'username: @{db_admin.username}\n'
            f'Имя: {db_admin.first_name}\n'
            f'Фамилия: {db_admin.last_name}\n'
            f'Номер телефона: {db_admin.phone_number}\n'
            f'ID канала: {db_admin.channel_id}\n'
            f"Дата создания: {formatted_date}"
        )
        buttons_new_admin = types.InlineKeyboardMarkup()
        delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_created_admin:{db_admin.id}")
        close_msg_button = types.InlineKeyboardButton("Скрыть", callback_data=f"close_msg")
        buttons_new_admin.add(delete_button).add(close_msg_button)
        await bot.send_message(chat_id=current_user.tg_id, text=message_text, reply_markup=buttons_new_admin)

    background_tasks.add_task(send_message_task)

    return db_admin

@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    admin = authenticate_user(form_data.username, form_data.password, db)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"id": admin.id, "email": admin.email, "tg_id": admin.tg_id, "username": admin.username}
    )
    response = TokenSchema( access_token=access_token, token_type="bearer")
    return response

@router.get('/me', response_model=AdminSchema)
async def get_own_info(current_user=Depends(get_current_user)):
    return current_user

@router.delete('/delete/admin/{admin_id}')
async def delete_admin(admin_id, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    db.delete(db_admin)
    db.commit()