# Version 0.3

import logging
from typing import Dict
from datetime import datetime
import json
import pickle

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

import os
from dotenv import load_dotenv
load_dotenv()

###########################################################

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_UPDATE, TYPING_REMOVE, TYPING_LIST, TYPING_COIN, TYPING_COORDS, FINAL = range(7)

reply_keyboard = [
    ['Add'],
    ['Remove'],
    ['List']
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

reply_keyboard_direction = [
    ['Above'],
    ['Below'],
]
markup_direction = ReplyKeyboardMarkup(reply_keyboard_direction, one_time_keyboard=True)

trendlines = {}

action = ''
coinName = ''
m, b = 0, 0
tempDirection = ''

def start(update: Update, context: CallbackContext) -> int:

    global trendlines

    try:
        trendlinesFile = open("trendlinesFile.pkl", "rb")
        trendlines = pickle.load(trendlinesFile)
    except:
        trendlinesFile = open("trendlinesFile.pkl", "wb")
        pickle.dump(trendlines, trendlinesFile)
        trendlinesFile.close()

    update.message.reply_text(
        "Hi! My name is Doctor Trendline. "
        "What do you want to do?",
        reply_markup=markup,
    )

    return CHOOSING
	
def add_action(update: Update, context: CallbackContext) -> int:

    global action
    action = 'Add'

    update.message.reply_text(
       f"What coin?\n"
    )

    return TYPING_COIN
	
def coin_action(update: Update, context: CallbackContext) -> int:

    global coinName

    #Received coin name
    text = update.message.text
    coinName = text

    update.message.reply_text(
        f"Good coin!\n"
		"What coords? (Format: 31-12-21 13:45, 02-01-22 17:30, 3.124, 3.251)",
    )

    return TYPING_COORDS
	
def direction_action(update: Update, context: CallbackContext) -> int:
    global m
    global b

    user_data = context.user_data
    text = update.message.text
    
    listOfCoords = text.split(", ")

    x1 = datetime.strptime(listOfCoords[0], '%d-%m-%y %H:%M')
    x2 = datetime.strptime(listOfCoords[1], '%d-%m-%y %H:%M')
    y1 = float(listOfCoords[2])
    y2 = float(listOfCoords[3])

    timestamp1=x1.timestamp()
    timestamp2=x2.timestamp()

    rise=y2-y1
    run=timestamp2-timestamp1

    m=rise/run
    b=y1-(m*timestamp1)

    update.message.reply_text(
        f"What direction?\n",
        reply_markup=markup_direction,
    )

    return FINAL
	
def final_action(update: Update, context: CallbackContext) -> int:
    global coinName
    text = update.message.text

    if action == 'Add':
        tempDirection = text

        if coinName not in trendlines:
            trendlines[coinName] = [[m,b,tempDirection]]
        else:
            trendlines[coinName].append([m,b,tempDirection])
    elif action == 'Remove':
        coinName, indexNum = text.split(" ")
        indexNum = int(indexNum)
        del trendlines[coinName][indexNum]

    trendlinesFile = open("trendlinesFile.pkl", "wb")
    pickle.dump(trendlines, trendlinesFile)
    trendlinesFile.close()

    print(trendlines)
    print(action)

    update.message.reply_text(
        f"Okay done!\n",
		reply_markup=markup,
    )

    return CHOOSING

def remove_action(update: Update, context: CallbackContext) -> int:
    global action
    action = 'Remove'

    update.message.reply_text(
        "What coin and trendline do you want to remove? (ie: BTC-USDT 2)"
    )

    return FINAL

def list_action(update: Update, context: CallbackContext) -> int:
    
    global action
    action = 'List'
    reply = json.dumps(trendlines, sort_keys=True, indent=4)

    update.message.reply_text(
        reply,
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f"Cancelled action.",
        reply_markup=markup,
    )
    
    return CHOOSING


def main() -> None:
    updater = Updater(os.environ.get('telegramBotToken'))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^(Add)$') & ~(Filters.command | Filters.regex('^Done$')), add_action),
                MessageHandler(Filters.regex('^(Remove)$') & ~(Filters.command | Filters.regex('^Done$')), remove_action),
                MessageHandler(Filters.regex('^(List)$') & ~(Filters.command | Filters.regex('^Done$')), list_action),
            ],
			
            TYPING_COIN: [
                MessageHandler(Filters.regex('^.*-[a-zA-Z]+$') & ~(Filters.command | Filters.regex('^Done$')), coin_action),
            ],

			TYPING_COORDS: [
                MessageHandler(Filters.regex('.*') & ~(Filters.command | Filters.regex('^Done$')), direction_action),
            ],
			
			FINAL: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), final_action),
            ],
			
            TYPING_UPDATE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    update_action,
                )
            ],
            TYPING_REMOVE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    remove_action,
                )
            ],
            TYPING_LIST: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    list_action,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()