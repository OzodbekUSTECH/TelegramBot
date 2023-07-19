from aiogram import types
from aiogram.types.web_app_info import WebAppInfo

def get_list_of_all_channels_statistics(curr_page, all_channels, channel = None):
    kb = types.InlineKeyboardMarkup()
    #кнопка чтобы перейти на канал надо сделать
    if channel is not None:
        channel_link = types.InlineKeyboardButton(text="Перейти в канал", url="https://t.me/+cS4PmYBjhltkNzgy" )
    closemsg = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_channel")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 2)}/{str(len(all_channels) + 1)}", callback_data='_')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_channel")
    if channel is not None:
        kb.add(closemsg, channel_link).add(backbtn, counter_text, nextbtn)
    else:
        kb.add(closemsg).add(backbtn, counter_text, nextbtn)

    return kb