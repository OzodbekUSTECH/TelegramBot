from aiogram import types
from aiogram.types.web_app_info import WebAppInfo

def get_btns_for_post(post):
    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    send_channel = types.InlineKeyboardButton("Отправить в канал", callback_data=f"confirm_send_to_chanel:{post.id}")
    send_users = types.InlineKeyboardButton("Отправить подписчикам", callback_data=f"confirm_send_to_subs:{post.id}")
    send_everywhere = types.InlineKeyboardButton("Отправить всем", callback_data=f'confirm_send_to_everywhere:{post.id}')
    if post.button_name:
        kb.add(post_btn).add(send_channel).add(send_users).add(send_everywhere)
    else:
        kb.add(send_channel).add(send_users).add(send_everywhere)

    return kb

def get_post_button(post):
    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=post.button_name, url=post.button_url)
    kb.add(post_btn)
    return kb