from aiogram import types
from aiogram.types.web_app_info import WebAppInfo

def get_started_buttons(superuser):
    kb = types.InlineKeyboardMarkup(resize_keyboard=True)
    create_admin = types.InlineKeyboardMarkup(text="Создать Админа", web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")) # страница для аккаунта
    get_list_of_admins = types.InlineKeyboardButton(text="Список Админов", callback_data="list_of_admins_show")
    kb.add(create_admin).add(get_list_of_admins)
    return kb



def get_list_of_all_admin(admin, curr_page, all_admins):
    kb = types.InlineKeyboardMarkup()
    closemsg = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    edit_btn = types.InlineKeyboardButton(text="Ред.",  web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")) #нужно будет динамично передать id админа
    deletebtn = types.InlineKeyboardButton(text="Удалить", callback_data=f"confirm_delete_admin:{admin.id}")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_post")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 1)}/{str(len(all_admins))}", callback_data='_')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_post")
    
    kb.add(closemsg, edit_btn, deletebtn).add(backbtn, counter_text, nextbtn)
    return kb

def delete_admin_or_not(admin_id):
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"delete_admin_from_list:{admin_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="cancel_delete_admin")
    kb.add(yes_btn, no_btn)
    return kb


def get_buttons_for_new_admin(db_admin):
    buttons_new_admin = types.InlineKeyboardMarkup()
    delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_created_admin:{db_admin.id}")
    edit_button = types.InlineKeyboardButton("Редактировать", web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")) #нужно будет динамично передать id админа и superadmin
    close_msg_button = types.InlineKeyboardButton("Скрыть", callback_data=f"close_msg")
    buttons_new_admin.add(delete_button, edit_button).add(close_msg_button)
    return buttons_new_admin