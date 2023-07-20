from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from bot import bot


async def get_channel_link(channel_id):
    try:
        chat = await bot.get_chat(channel_id)
        if chat.type == types.ChatType.CHANNEL:
            return chat.invite_link
    except Exception:
        return None
    

def get_list_of_all_channels_statistics(curr_page, all_channels, channel = None, link_channel = None):
    kb = types.InlineKeyboardMarkup()
    #кнопка чтобы перейти на канал надо сделать
    
    channel_link = types.InlineKeyboardButton(text="Перейти в канал", url=link_channel)

   
    closemsg = types.InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")
    backbtn = types.InlineKeyboardButton(text="⬅️", callback_data="prev_channel")
    counter_text = types.InlineKeyboardButton(text=f"{str(curr_page + 2)}/{str(len(all_channels) + 1)}", callback_data='_')
    nextbtn = types.InlineKeyboardButton(text="➡️", callback_data="next_channel")
    if channel is not None and link_channel is not None:
        kb.add(closemsg, channel_link).add(backbtn, counter_text, nextbtn)
    elif link_channel is None:

        change_channel_id = types.InlineKeyboardButton(
            text="Изменить",
            web_app=WebAppInfo(url=f"https://rdz-science.com/blog_detail/166/")
        )
        kb.add(closemsg, change_channel_id).add(backbtn, counter_text, nextbtn)
    else:
        kb.add(closemsg).add(backbtn, counter_text, nextbtn)

    return kb




