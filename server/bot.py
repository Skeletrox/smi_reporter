import os
from telegram.ext import Updater, CommandHandler
from telegram import Chat
import pickle
import json
import re
from poller import InfluxPoller, pollForGraphs

compiledRange = re.compile(r"\d+[h|m|s|d|w|m|y]")

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
    deviceID = update.message.text.replace("/link", '').strip()
    dtcObj = None
    try:
        with open("./device_to_chat.json", "r") as dtc:
            dtcObj = json.loads(dtc.read())
    except Exception:
        dtcObj = {}
        
    dtcObj[deviceID] = chatID

    with open('./device_to_chat.json', 'w') as dtc:
        dtc.write(json.dumps(dtcObj))

    bot.sendMessage(chat_id=chatID, text="Device {} has been linked to this chat!".format(deviceID))


def help(bot, update):
    helpString = '''
    Hi! Welcome to the reporter bot! These are the following commands you can use to run this:

    /hello: Saves your chat to disk so that the bot knows whom to notify when it has to.

    /link <deviceid>: Links a deviceid to this chat. 

    /graph <deviceid> <timerange>: Plots a utilization graph for deviceid over the past timerange amount of time. Timerange has to be in InfluxQL format.
    '''
    bot.sendMessage(chat_id=update.message.chat_id, text=helpString)



def queryGraph(bot, update):
    request = update.message.text
    parts = request.split(' ')
    if len(parts) < 3:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please query as /graph <device_id> <time_range>")
        return

    deviceID = parts[1]
    timeRange = parts[2]
    if compiledRange.match(timeRange) is None:
        bot.sendMessage(chat_id=update.message.chat_id, text="Please set your time range as <number><d/w/m/y/h/m/s/>, eg. 15d, 12h, etc. You submitted: {}".format(timeRange))
        return
    result = None
    try:
        result = pollForGraphs(deviceID, timeRange)
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text="Getting data failed with error: {}".format(str(e)))
        return
    if result is None:
        bot.sendMessage(chat_id=update.message.chat_id, text="No data for the device ID and time range")
        return
    bot.send_photo(chat_id=update.message.chat_id, photo=open('./{}.png'.format(deviceID), 'rb'), text="Data for {} in the last {}".format(deviceID, timeRange))
    

hello_handler = CommandHandler("hello", hello)
link_handler = CommandHandler("link", linkIDtoChat)
graph_handler = CommandHandler("graph", queryGraph)
help_handler = CommandHandler("help", help)


dispatcher.add_handler(hello_handler)
dispatcher.add_handler(link_handler)
dispatcher.add_handler(graph_handler)
dispatcher.add_handler(help_handler)

try:
    InfluxPoller().start()
    updater.start_polling()
except Exception as e:
    print(e)