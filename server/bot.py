import os
from telegram.ext import Updater, CommandHandler
from telegram import Chat
import pickle
import json
from poller import InfluxPoller

token = os.getenv("NVIDIA_BOT_TOKEN")

updater = Updater(token=token)
dispatcher = updater.dispatcher


def hello(bot, update):
    chatID = update.message.chat_id
    botAndUpdate = {
        "bot": bot,
        "update": update
    }
    try:
        val = pickle.dumps(botAndUpdate)
        with open("botAndUpdate_{}.bau".format(chatID), "wb") as baubau:
            baubau.write(val)
    except Exception as e:
        print(e)
    bot.sendMessage(chat_id=chatID, text="Hello! ID is {}".format(chatID))



def linkIDtoChat(bot, update):
    chatID = update.message.chat_id
    deviceID = update.message.text.replace('/link', '').strip()
    dtcObj = None
    try:
        with open('./device_to_chat.json', 'r') as dtc:
            dtcObj = json.loads(dtc.read())
    except Exception:
        dtcObj = {}
        
    dtcObj[deviceID] = chatID

    with open('./device_to_chat.json', 'w') as dtc:
        dtc.write(json.dumps(dtcObj))

    bot.sendMessage(chat_id=chatID, text="Device {} has been linked to this chat!".format(deviceID))
    
    

hello_handler = CommandHandler("hello", hello)
link_handler = CommandHandler("link", linkIDtoChat)

dispatcher.add_handler(hello_handler)
dispatcher.add_handler(link_handler)

try:
    InfluxPoller().start()
    updater.start_polling()
except Exception as e:
    print(e)