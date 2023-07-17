from aiogram import types

list_of_admins = types.ReplyKeyboardMarkup(resize_keyboard=True)
get_list_of_admins = types.KeyboardButton("Список Админов")
list_of_admins.add(get_list_of_admins)