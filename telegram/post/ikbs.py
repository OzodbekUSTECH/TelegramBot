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


def get_btns_for_pagination_posts(planned_post, curr_page, all_planned_posts):
    kb = types.InlineKeyboardMarkup()
    post_btn = types.InlineKeyboardButton(text=planned_post.button_name, url=planned_post.button_url)
    closemsg = types.InlineKeyboardButton(text="Скрыть", callback_data="close_msg")
    edit_btn = types.InlineKeyboardButton(text="Ред.",  web_app=WebAppInfo(url="https://habr.com/ru/articles/586494/")) #нужно будет динамично передать id админа
    deletebtn = types.InlineKeyboardButton(text="Удалить", callback_data=f"confirm_delete_planned_post:{planned_post.id}")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_post")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 1)}/{str(len(all_planned_posts))}", callback_data='__')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_post")
    
    if planned_post.button_name:
        kb.add(post_btn).add(closemsg, edit_btn, deletebtn).add(backbtn, counter_text, nextbtn)
    else:
        kb.add(closemsg, edit_btn, deletebtn).add(backbtn, counter_text, nextbtn)
    return kb

def delete_planned_post(planned_post_id):
    kb = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data=f"delete_planned_post_from_list:{planned_post_id}")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="cancel_delete_planned_post")
    kb.add(yes_btn, no_btn)
    return kb