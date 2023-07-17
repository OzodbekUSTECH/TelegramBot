from aiogram import types

list_of_admins = types.InlineKeyboardMarkup(resize_keyboard=True)
get_list_of_admins = types.InlineKeyboardButton(text="Список Админов", callback_data="list_of_admins_show")
list_of_admins.add(get_list_of_admins)



def get_list_of_all_admin(admin, curr_page, all_admins):
    kb = types.InlineKeyboardMarkup()
    closemsg = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    deletebtn = types.InlineKeyboardButton(text="Удалить", callback_data=f"confirm_delete_admin:{admin.id}")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_post")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 1)}/{str(len(all_admins))}", callback_data='_')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_post")
    
    kb.add(closemsg, deletebtn).add(backbtn, counter_text, nextbtn)
    return kb

def delete_admin_or_not(admin_id):
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"delete_admin_from_list:{admin_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="cancel_delete_admin")
    kb.add(yes_btn, no_btn)
    return kb