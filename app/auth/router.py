from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from database.db import get_db
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils import *
from sqlalchemy.exc import IntegrityError
from app.auth.schema import *
from bot import bot
from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from telegram.superuser.inlinekeyboards import get_buttons_for_new_admin

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
            f'Супер Админ: {db_admin.is_superuser}\n'
            f"Дата создания: {formatted_date}"
        )
        btns = get_buttons_for_new_admin(db_admin)
        await bot.send_message(chat_id=current_user.tg_id, text=message_text, reply_markup=btns, parse_mode="HTML")

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
    if current_user.is_superuser == False:
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа.")
    
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    db.delete(db_admin)
    db.commit()

@router.put('/admin/{admin_id}', name="update admin data", response_model=AdminSchema)
async def update_admin_data(admin_id: int, admin_update: AdminUpdateSchema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_superuser == False:
        raise HTTPException(status_code=403, detail="Недостаточно прав доступа.")
    
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if admin_update.tg_id is not None:
        db_admin.tg_id = admin_update.tg_id
    if admin_update.email is not None:
        db_admin.email = admin_update.email
    if admin_update.username is not None:
        db_admin.username = admin_update.username
    if admin_update.first_name is not None:
        db_admin.first_name = admin_update.first_name
    if admin_update.last_name is not None:
        db_admin.last_name = admin_update.last_name
    if admin_update.phone_number is not None:
        db_admin.phone_number = admin_update.phone_number
    if admin_update.channel_id is not None:
        db_admin.channel_id = admin_update.channel_id
    if admin_update.is_superuser is not False:
        db_admin.is_superuser = admin_update.is_superuser

    db.commit()

    return db_admin

@router.get('admin/{admin_id}', name="get admin by id", response_model = AdminSchema)
async def get_admin_by_id(admin_id: int, db: Session = Depends(get_db)):
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not a superuser")
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found. dont exist")
    return db_admin


@router.put("/admin/me/update", response_model=AdminSchema, tags=['Own DATA'])
async def change_own_data(background_tasks: BackgroundTasks,new_data = UpdateOwnAdminSchema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == current_user.id).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not an admin")
    if new_data.email is not None:
        db_admin.email = new_data.email
    if new_data.username is not None:
        db_admin.username = new_data.username
    if new_data.first_name is not None:
        db_admin.first_name = new_data.first_name
    if new_data.last_name is not None:
        db_admin.last_name = new_data.last_name
    if new_data.phone_number is not None:
        db_admin.phone_number = new_data.phone_number
    if new_data.channel_id is not None:
        db_admin.channel_id = new_data.channel_id

    db.commit()
    db.refresh(db_admin)

    # super_users = db.query(models.Admin).filter(models.Admin.is_superuser == True, models.Admin.tg_id != current_user.tg_id).all()

    # async def send_message_task():
        
    #     message_text = (
    #         "Данные были изменены:\n\n"
    #         f'Номер Админа: {db_admin.id}\n'
    #         f'ID tg: {db_admin.tg_id}\n'
    #         )
    #     has_changes = False  # Variable to track if there are any changes
        
    #     # Helper function to check if a field is updated and add it to the message_text
    #     def add_change(field_name, prev_value, new_value):
    #         nonlocal message_text, has_changes
    #         if prev_value != new_value:
    #             message_text += f"{field_name}:\n{prev_value} => {new_value}\n"
    #             has_changes = True

    #     add_change("email", prev_data.email, db_admin.email)
    #     add_change("username", prev_data.username, f"@{db_admin.username}")
    #     add_change("Имя", prev_data.first_name, db_admin.first_name)
    #     add_change("Фамилия", prev_data.last_name, db_admin.last_name)
    #     add_change("Номер телефона", prev_data.phone_number, db_admin.phone_number)
    #     add_change("ID канала", prev_data.channel_id, db_admin.channel_id)

    #     # If no changes, just display the data without any indication of change
    #     if not has_changes:
    #         message_text += (
    #             f'Номер Админа: {db_admin.id}\n'
    #             f'ID tg: {db_admin.tg_id}\n'
    #         )

    #     btns = types.InlineKeyboardMarkup()
    #     close_msg_button = types.InlineKeyboardButton("Скрыть", callback_data=f"close_msg")
    #     btns.add(close_msg_button)
        
    #     await bot.send_message(chat_id=current_user.tg_id, text=message_text, reply_markup=btns, parse_mode="HTML")
    #     for superuser in super_users:
    #         await bot.send_message(chat_id=superuser.tg_id, text=message_text, reply_markup=btns, parse_mode="HTML")

    # background_tasks.add_task(send_message_task)

    return db_admin