#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sys
import telepot
import time
from telepot.loop import MessageLoop

def save_status(obj):
    with open('chats.json', 'w') as f:
        f.write(json.dumps(obj))

def save_allowed(s):
    with open('allowed.json', 'w') as f:
        f.write(json.dumps(list(s)))

if not os.path.isfile('chats.json'):
    save_status({})

if not os.path.isfile('allowed.json'):
    save_allowed(set())

chats = {}
allowed = []
TOKEN = ""
PASSWORD = "changeme"

with open('chats.json', 'r') as f:
    chats = json.load(f)

with open('allowed.json', 'r') as f:
    allowed = set(json.load(f))

if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)
        if config['token'] == "":
            sys.exit("No token defined. Define it in a file called config.json.")
        if config['password'] == "":
            print("WARNING: Empty Password for registering to use the bot." +
                  " It could be dangerous, because anybody could use this bot" +
                  " and forward messages to the channels associated to it")
        TOKEN = config['token']
        PASSWORD = config['password']
else:
    sys.exit("No config file found.")

def is_allowed(msg):
    if msg['chat']['type'] == 'channel':
        return True #all channel admins are allowed to use the bot (channels don't have sender info)
    return 'from' in msg and msg['from']['id'] in allowed

def handle(msg):
    print("Message: " + str(msg))
    # Add person as allowed
    content_type, chat_type, chat_id = telepot.glance(msg)
    txt = ""
    if 'text' in msg:
        txt = txt + msg['text']
    elif 'caption' in msg:
        txt = txt + msg['caption']
    # Addme and rmme only valid on groups and personal chats.
    if msg['chat']['type'] != 'channel':
        if "/addME" == txt.strip()[:6]:
            if msg['chat']['type'] != 'private':
                bot.sendMessage(chat_id, "Эта команда предназначена для использования только в личных чатах.")
            else:
                used_password = " ".join(txt.strip().split(" ")[1:])
                if used_password == PASSWORD:
                    allowed.add(msg['from']['id'])
                    save_allowed(allowed)
                    bot.sendMessage(chat_id, msg['from']['first_name'] + ", успешно дабпвлен " +
                                    "В группу техников БМ.")
                else:
                    bot.sendMessage(chat_id, "Даже пароль Ввести не можешь.")
        if "/rmME" == txt.strip()[:5]:
            allowed.remove(msg['from']['id'])
            save_allowed(allowed)
            bot.sendMessage(chat_id, "Уволен нах...")
    if is_allowed(msg):
        if txt != "":
            if "/add " == txt[:5]:
                txt_split = txt.strip().split(" ")
                if len(txt_split) == 2 and "#" == txt_split[1][0]:
                    tag = txt_split[1].lower()
                    name = ""
                    if msg['chat']['type'] == "private":
                        name = name + "Магазин " + msg['chat']['first_name'] + ((" " + msg['chat']['last_name']) if 'last_name' in msg['chat'] else "")
                    else:
                        name = msg['chat']['title']
                    chats[tag] = {'id': chat_id, 'name': name}
                    bot.sendMessage(chat_id, " Добавлен " + name + tag)
                    save_status(chats)
                else:
                    bot.sendMessage(chat_id, "Не правельный формат. Должно быть так _/add #Номер магаза_", parse_mode="Markdown")
            elif "/rm " == txt[:4]:
                txt_split = txt.strip().split(" ")
                if len(txt_split) == 2 and "#" == txt_split[1][0]:
                    tag = txt_split[1].lower()
                    if tag in chats:
                        if chats[tag]['id'] == chat_id:
                            del chats[tag]
                            bot.sendMessage(chat_id, "Магазин "+tag+" удален из твоего списка.")
                            save_status(chats)
                            return
                        else:
                            bot.sendMessage(chat_id, "Ты можешь удалить магазин из другого Чата.")
                    else:
                        bot.sendMessage(chat_id, "Магаза нет в списке")
                else:
                    bot.sendMessage(chat_id, "Не правельный формат. Должно быть так _/rm #Номер магаза_,", parse_mode="Markdown")

            elif "/Market" ==  txt.strip()[:8]:
                tags_names = []
                for tag, chat in chats.items():
                    tags_names.append( (tag, chat['name']))
                response = "<b>Мои магазины</b>"
                for (tag, name) in sorted(tags_names):
                    response = response + "\n<b>" + tag + "</b>: <i>" + name + "</i>"
                bot.sendMessage(chat_id, response, parse_mode="HTML")
            elif "#" == txt[0]:
                txt_split =txt.strip().split(" ")
                i = 0
                tags = []
                while i < len(txt_split) and txt_split[i][0] == "#":
                    tags.append(txt_split[i].lower())
                    i+=1
                if i != len(txt_split) or 'reply_to_message' in msg:
                    approved = []
                    rejected = []
                    for tag in tags:
                        if tag in chats:
                            if chats[tag]['id'] != chat_id:
                                approved.append(chats[tag]['name'])
                                bot.forwardMessage(chats[tag]['id'], chat_id, msg['message_id'])
                                if 'reply_to_message' in msg:
                                    bot.forwardMessage(chats[tag]['id'], chat_id, msg['reply_to_message']['message_id'])
                        else:
                            rejected.append(tag)
                    if len(rejected) > 0:
                        bot.sendMessage(chat_id, " Ошибка ! Заявка не отправлена  <i>" + ", ".join(rejected) + "</i>", parse_mode="HTML")
                else:
                    bot.sendMessage(chat_id, "Не удалось отправить сообщение с тегом '#' , которые не являются ответом на другое сообщение")

bot = telepot.Bot(TOKEN)

MessageLoop(bot, handle).run_as_thread()
print('Загрузка ...')
# Keep the program running.
while 1:
    time.sleep(10)

