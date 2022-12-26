## Started Building (telegram-bot-api v20.x): December 5, 2022  4:19
#********************************************* OpenAI for Telegram -- Text Completion *****************************************************
from telegram.ext import Updater
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import InlineQueryHandler
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import filters
from telegram import Bot
from telegram.ext import PicklePersistence
from telegram.ext import Application

import asyncio

from _telegramOpenAIComds import *
from _reqOpenAI import *
from _BotInlineQuery import *
# from _userSettings import *

#! Bot API Key  -- using environment variable (from .env file) to avoid exposing the API key in the code
BOT_TOKEN = config('TELE_BOT_API_KEY_2')
bot = Bot(BOT_TOKEN)

#* Global Variables
COM_TXT = []
COM_KEYS = []
OPENAI_KEYS = []

# Enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(module)s - %(funcName)s - ln %(lineno)d - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

#? Load The Command text that will used later by /help, /commands, etc
def load_commands_text():
    import json
    global OPENAI_KEYS, COM_KEYS, COM_TXT
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
        MainComm = my_data.keys()
        OPENAI_KEYS = list(my_data['OpenAICommands'].keys())
        COM_KEYS = list(my_data['BotCommands'].keys())
        for i, Mkey in enumerate(MainComm): 
            Comm = my_data[Mkey].keys()
            nkeys = len(Comm)
            text = ''
            for key in Comm:
                nkeys -= 1
                text = text + '• ' + '<b>' + key.title() + '</b>' + ' - ' + my_data[Mkey][key][0]
                if nkeys != 0:
                    text = text + '\n'
            COM_TXT.append(text)

#? Add To User Info to Database (if new-user)
async def new_user (update: Update):
    chat_id = str(update.message.chat_id)
    try:
        #* User DataBase
        import json
        with open("_usersInfo.json", "r") as file:
            info_data = json.load(file)
        backup_info_data = info_data
        
        #* User Default Settings
        with open('_userSettings.json', "r") as file:
            sett_data = json.load(file)
        backup_sett_data = sett_data
        try:
            #* Check if user already exist in database
            if (info_data.get(chat_id) is None):
                #* User Info
                type = update.message.chat.type
                username = update.message.chat.username
                first_name = update.message.chat.first_name
                last_name = update.message.chat.last_name
                from datetime import datetime
                UserInfo = {
                    'type': type,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'time': str(datetime.now())
                }
                #* Add User
                info_data[chat_id] = UserInfo
                with open("_usersInfo.json", 'w') as file:
                    json.dump(info_data, file, indent=4)
                    
                #* Give the User (New) Default Settings
                sett_data[chat_id] = sett_data['defualt_settings']
                with open('_userSettings.json', "w") as file:
                    json.dump(sett_data, file, indent=4)
                
                #* Prompt to User
                await update.message.reply_text(f"Welcome {first_name}! 😀")                                              # Welcome User
            else:
                #* Prompt to User
                await update.message.reply_text(f"Welcome Back {info_data[chat_id]['first_name']}! 😀")                   # Welcome User
        except Exception as err:
            logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
            #! Incase something went wrong use we won't lose our user's Information (and Settings)
            with open("_usersInfo.json", 'w') as file:
                json.dump(backup_info_data, file, indent=4)
            with open('_userSettings.json', "w") as file:
                json.dump(backup_sett_data, file, indent=4)
            return False
    except Exception as err:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
        return False
    return True

#* Main Menu Keyboard (Inline)
Main_Menu_Buttons = [
    [
        InlineKeyboardButton("🗨️ Text Generation!", callback_data=str(ONE))
    ],
    [
        InlineKeyboardButton("🎴 Image Generation!", callback_data=str(TWO))
    ],
    [
        InlineKeyboardButton("🔆 Help", callback_data=str(THREE)),
        InlineKeyboardButton("⛏ Change Settings", callback_data=str(FOUR)),
    ],
    [
        InlineKeyboardButton("⚙️ Current Settings", callback_data=str(FIVE)),
        InlineKeyboardButton("🧰 Default Settings", callback_data=str(SIX)),
    ],
    [
        InlineKeyboardButton("💡Command Info", callback_data=str(SEVEN)),
        InlineKeyboardButton("❤ Contact", callback_data=str(EIGHT))
    ],
    [
        InlineKeyboardButton("🔸 ChatAI", url='https://chatai.typedream.app/')
    ]
]

Settings_Buttons = [
    [
        InlineKeyboardButton("model", callback_data=str(ONE)),
        InlineKeyboardButton("temperature", callback_data=str(TWO))
    ],
    [
        InlineKeyboardButton("max_length", callback_data=str(THREE)),
        InlineKeyboardButton("stop", callback_data=str(FOUR)),
    ],
    [
        InlineKeyboardButton("top_p", callback_data=str(FIVE)),
        InlineKeyboardButton("frequency_penalty", callback_data=str(SIX)),
    ],
    [
        InlineKeyboardButton("presence_penalty", callback_data=str(SEVEN)),
        InlineKeyboardButton("best_of", callback_data=str(EIGHT))
    ],
    [
        InlineKeyboardButton("n", callback_data=str(NINE)),
        InlineKeyboardButton("gen_probs", callback_data=str(TEN))
    ],
    [
        InlineKeyboardButton("💡Get Info", callback_data=str(ELEVEN))
    ],
    [
        InlineKeyboardButton("🏠 Main Menu", callback_data=str(CANCELOPT))
    ]
]
    
#? Used when /start or any random user message is send -- Text Message
async def BotOptions (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Show Main Menu
    inline_markup = InlineKeyboardMarkup(Main_Menu_Buttons)
    await update.message.reply_text("Choose What You Would Like To Do? 😀", reply_markup=inline_markup)
    #? Un-pin all messages from chat
    chat_id = str(update.message.chat_id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN

#? When Setting Canceled is pressed -- Callback
async def BotOptionsCallBack (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Show Main Menu
    inline_markup = InlineKeyboardMarkup(Main_Menu_Buttons)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Choose What You Would Like To Do? 😀", reply_markup=inline_markup)
    #? Un-pin all messages from chat
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN

#? Generate in separate message -- Callback
async def BotOptionsCallApart (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Show Main Menu
    inline_markup = InlineKeyboardMarkup(Main_Menu_Buttons)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Choose What You Would Like To Do? 😀", reply_markup=inline_markup)
    #? Un-pin all messages from chat
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN
    
#? Start
async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):    
    #* Add New User
    status = await new_user(update)
    
    #* Prompt to User
    if status:
        await update.message.reply_text(f'''
Hello!, Welcome to <a href='https://chatai.typedream.app/'>ChatAI</a> 😊
I can help you with Text Completion - This Bot is based on <a href='https://bit.ly/OpenAI_Introduction'>OpenAI</a>
'''
            , disable_web_page_preview=True
            , parse_mode='HTML'
        )
        return await BotOptions (update, context)
    else:
        #* Prompt Error to User and End the Conversation
        await update.message.reply_text("⚠ Oops! Something went wrong, please try again /start")
        return ConversationHandler.END

#? When Help is pressed
async def help (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Prompt to User
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'''
Hello there! 😀 
<a href='https://chatai.typedream.app/'>ChatAI</a> is a Telegram Bot that can help you with Text Completion.

The Bot uses powerful <a href='https://bit.ly/OpenAI_Introduction'>OpenAI</a> and generates Text Completion right here in Telegram.
<b>ChatAI is OpenAI but for Telegram.</b>

• <b>Chat :</b> Start Chatting (Text Completion)
• <b>Change Settings :</b> Alter Your Settings For Text Completion!
• <b>Current Settings :</b> Check Your Settings For Text Completion!
• <b>Default Settings :</b> Fall Back To Default Settings!
• <b>Command Info :</b> Learn About Different Settings!
'''
        , disable_web_page_preview=True
        , parse_mode='HTML'
    )
    #* Show Main Menu
    return await BotOptionsCallApart (update, context)

#? When Chat is pressed
async def chat (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Prompt to User
    await update.callback_query.answer()
    openMsg = await update.callback_query.edit_message_text(
        text="🔸 OpenAI - Text Completion.", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data=str(CANCELOPT))]])
    )
    #* Pin the chat cancel message
    chat_id = openMsg.chat_id
    msg_id = openMsg.message_id
    await bot.pin_chat_message(chat_id = chat_id, message_id = msg_id)
    #* Show Reply-Keyboard with Examples
    reply_keyboard = [
        ["Write a tagline for an ice cream shop."],
        ["Write a code for Pyramid in Python."],
        ["How to get famous?"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.callback_query.message.reply_text("• Try writting something like:\n<b>\"Write a tagline for an ice cream shop.\"</b>\n<a href='https://bit.ly/OpenAIPlay'>OpenAI Playground</a>", disable_web_page_preview=True, parse_mode='HTML', reply_markup=reply_markup)
    #* Tell ConversationHandler that we're in state `CHAT` now
    return CHAT

#? When Image is pressed
async def image (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Prompt to User
    await update.callback_query.answer()
    openMsg = await update.callback_query.edit_message_text(
        text="🔸 OpenAI - Image Generation.", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data=str(CANCELOPT))]])
    )
    #* Pin the image cancel message
    chat_id = openMsg.chat_id
    msg_id = openMsg.message_id
    await bot.pin_chat_message(chat_id = chat_id, message_id = msg_id)
    #* Show Reply-Keyboard with Examples
    reply_keyboard = [
        ["A cute chow chow dog with birthday hat."],
        ["A sunlit indoor lounge area with a pool containing a flamingo."]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.callback_query.message.reply_text("• Try writting something like:\n<b>\"A cute chow chow dog with birthday hat.\"</b>\n<a href='https://bit.ly/OpenAIPlay'>OpenAI Playground</a>", disable_web_page_preview=True, parse_mode='HTML', reply_markup=reply_markup)
    #* Tell ConversationHandler that we're in state `IMAGE` now
    return IMAGE

#? Chat Intialize
async def chat_intial (update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await openai_intial (update, context, type=0)
#? Image Intialize
async def image_intial (update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await openai_intial (update, context, type=1)

#? OpenAI Intialize
async def openai_intial (update: Update, context: ContextTypes.DEFAULT_TYPE, type=0):
    #* Prompt Generate Message to User
    gen_msg = await update.message.reply_text(
        "Generating...",
        reply_markup=ReplyKeyboardRemove(),
    )
    #* Call OpenAI Handler for futher instruction to API
    return await openai_handler (update, context, gen_msg, type=type)

#? OpenAI Handler
async def openai_handler (update: Update, context: ContextTypes.DEFAULT_TYPE, gen_msg, type=0):
    text = update.message.text
    chat_id = str(update.message.chat_id)
    try:
        #* Send Chat OpenAI request
        if (type==0):
            try:
                response, prob_file = await send_req_openai_chat(update, text, chat_id, False)
            except Exception as err:
                logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
                await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)      # Delete "Generating..." message
                await update.message.reply_text("⚠ " + str(err) + "\nTry Again")
            else:
                await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)      # Delete "Generating..." message
                #* Prompt OpenAI Response to User if generated else raise error
                await update.message.reply_text(response)
                #* Send Probability File
                if (prob_file != None):
                    with open(prob_file, 'rb') as doc:
                        await context.bot.send_document(chat_id, doc)
                    import os
                    os.remove(prob_file)        # Delete Probability File
                #* If user's first query of the day, give a Tip to change settings
                with open('_userSettings.json', "r") as file:
                    data = json.load(file)
                if data[chat_id]['num_openai_req'] == 1:
                    await update.message.reply_text("💡Tips:\n• You can change settings for Text Generation using 'Change Settings' from Main Menu\n• Use '🏠 Main Menu' from above pinned to go back")
        #* Send Image OpenAI request
        else:
            #* The maximum length is 1000 characters. (950 for buffer)
            if (len(text)>950):
                await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)          # Delete "Generating..." message
                await update.message.reply_text("❗ Query too long (The maximum length is 1000 characters.)")
            else:
                try:
                    response, limit = await send_req_openai_image(update, text, chat_id, False)
                except Exception as err:
                    logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
                    await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)      # Delete "Generating..." message
                    await update.message.reply_text("⚠ " + str(err) + "\nTry Again")
                else:
                    await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)      # Delete "Generating..." message
                    #* Prompt OpenAI Response to User if generated else raise error
                    if (not limit): await context.bot.send_photo(chat_id=chat_id, photo=response)
                    else: await update.message.reply_text(response)
    except Exception as err:    
        #* Prompt Error
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
        await update.message.reply_text("⚠ Oops! Unexpected Error Occured.\n• But you can keep Writing! 😀\n• Or use '🏠 Main Menu' from above pinned to go back")
    finally:
        if (type==0):
            #* Tell ConversationHandler that we're in state `CHAT` now
            return CHAT
        else:
            #* Tell ConversationHandler that we're in state `IMAGE` now
            return IMAGE

#? Terminate OpenAI and Show Main Menu
async def TerminateOpenAI (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    #* Prompt Terminate Message to User and **Remove any Reply-Keyboard**
    gen_msg = await update.callback_query.message.reply_text(
        "🏠 Going Back Home..😊",
        reply_markup=ReplyKeyboardRemove(),
    )
    #* Un-pin all messages from chat -- the cancel message
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Delete Generated Message
    await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)
    #* Show Main Menu
    inline_markup = InlineKeyboardMarkup(Main_Menu_Buttons)
    await update.callback_query.message.reply_text("Choose What You Would Like To Do? 😀", reply_markup=inline_markup)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN
    
#? Quick Settings
async def settings (update: Update, context: ContextTypes.DEFAULT_TYPE, isText=False):
    #* Prompt Settings Menu to User
    inline_markup = InlineKeyboardMarkup(Settings_Buttons)
    if (not isText):            # When called from Callback -- replace previous prompt
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Select the setting, you want to Change.", reply_markup=inline_markup)
    else:                     # When called from _text() functions
        try:
            await update.message.reply_text("Select the setting, you want to Change.", reply_markup=inline_markup)
        except:                 # When called from Callback -- make new prompt
            await update.callback_query.answer()
            await update.callback_query.message.reply_text("Select the setting, you want to Change.", reply_markup=inline_markup)
    #* Tell ConversationHandler that we're in state `SETTINGS` now
    return SETTINGS

#? Error occured while making change in Settings
async def comd_try_again (update: Update, context: ContextTypes.DEFAULT_TYPE, text, callback_val, isText=False):
    #* Prompt Error and its Options
    inline_keyboard = [
        [
            InlineKeyboardButton("🔄 Try Again!", callback_data=str(callback_val)),
            InlineKeyboardButton("❌CANCEL", callback_data=str(CANCELOPT-1)),
        ]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    if (not isText):            # When called from Callback -- replace previous prompt
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=inline_markup)
    else:                       # When called from _text() functions
        await update.message.reply_text(text, reply_markup=inline_markup)
    #* Transfer control to ConversationHandler's' state `SETTINGS` again
    return SETTINGS

#? Update User Settings
async def Update_Command_Value (update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, new_val, comd, err_text, callback_val, isText=False):
    #* Retrieve user's settings
    filename = '_userSettings.json'
    with open(filename, "r") as f:
        data = json.load(f)
    Backup_Data = data
        
    try:
        data[chat_id][comd] = new_val                                    #******** Update comd's value **********
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        if (not isText):            # When called from Callback -- replace previous prompt
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text = f"✅ Done! {comd} changed to: {new_val}")
            return await settings (update, context)           # Call settings and show Settings Menu
        else:                       # When called from _text() functions
            await update.message.reply_text(text = f"✅ Done! {comd} changed to: {new_val}")
            return await settings (update, context, True)     # Call settings and show Settings Menu
    except Exception as err:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
        #! Incase any Error occurs, we don't lose our user data
        with open(filename, "w") as f:
            json.dump(Backup_Data, f, indent=4)
        return await comd_try_again(update, context, err_text, callback_val, isText)

#? Update Model via Inline 
async def model_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']

    #? "text-davinci-003" the max_token is 4096, while for other models it is 2048
    if (new_val != "text-davinci-003"):
        curr_max_length = comd_val(chat_id, 'max_length')
        if (curr_max_length[0] > 2048):            
            try:
                filename = '_userSettings.json'
                with open(filename, "r") as f:
                    data = json.load(f)
                Backup_Data = data
                data[chat_id]['max_length'] = 2048
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)
            except Exception as err:
                logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
                with open(filename, "w") as f:                      #! Incase any Error occurs, we don't lose our user data
                    json.dump(Backup_Data, f, indent=4)
                return await comd_try_again(update, context, "⚠ Oops! Unexpected Error Occured. 😟", ONE)

    #* Update Model
    return await Update_Command_Value (update, context, chat_id, new_val, 'model', "⚠ Oops! Unexpected Error Occured. 😟", ONE)

#? When Model via User Text Input
async def model_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #*Try Again when any text is entered for Model
    return await comd_try_again(update, context, '❗ Choose from Options', ONE, True)

#? Update Gen_Probs via Inline
async def gen_probs_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = CANCELOPT if (update['callback_query']['data']==str(CANCELOPT)) else True if (update['callback_query']['data']=="True") else False
    
    #* Update Gen_Probs
    return await Update_Command_Value (update, context, chat_id, new_val, 'gen_probs', "⚠ Oops! Unexpected Error Occured. 😟", TEN)

#? When Gen_Probs via User Text Input
async def gen_probs_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #*Try Again when any text is entered for Gen_Probs
    return await comd_try_again(update, context, '❗ Choose from Options', TEN, True)

#? Update Temperature via Inline
async def temp_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = float(update['callback_query']['data'])
    
    #* Update Temperature
    return await Update_Command_Value (update, context, chat_id, new_val, 'temperature', "⚠ Oops! Unexpected Error Occured. 😟", TWO)

#? Update Temperature via User Text Input      
async def temp_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text

    #* Retrieve temperature's range
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    available_options = my_data["OpenAICommands"]['temperature'][1]
       
    new_val = float(new_val)    # raise error if text
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Temperature
        return await Update_Command_Value (update, context, chat_id, new_val, 'temperature', "⚠ Oops! Unexpected Error Occured. 😟", TWO, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", TWO, True)

#? Update Top_P via Inline
async def top_p_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = float(update['callback_query']['data'])
    
    #* Update Top_P
    return await Update_Command_Value (update, context, chat_id, new_val, 'top_p', "⚠ Oops! Unexpected Error Occured. 😟", FIVE)

#? Update Top_P via User Text Input
async def top_p_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text

    #* Retrieve top_p's range
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    available_options = my_data["OpenAICommands"]['top_p'][1]
        
    new_val = float(new_val)    # raise error if text
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Top_P
        return await Update_Command_Value (update, context, chat_id, new_val, 'top_p', "⚠ Oops! Unexpected Error Occured. 😟", FIVE, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", FIVE, True)

#? Update Frequency_Penalty via Inline
async def freq_penal_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = float(update['callback_query']['data'])
    
    #* Update Frequency_Penalty
    return await Update_Command_Value (update, context, chat_id, new_val, 'frequency_penalty', "⚠ Oops! Unexpected Error Occured. 😟", SIX)

#? Update Frequency_Penalty via User Text Input   
async def freq_penal_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text

    #* Retrieve frequency_penalty's range
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    available_options = my_data["OpenAICommands"]['frequency_penalty'][1]
       
    new_val = float(new_val)    # raise error if text
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Frequency_Penalty
        return await Update_Command_Value (update, context, chat_id, new_val, 'frequency_penalty', "⚠ Oops! Unexpected Error Occured. 😟", SIX, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SIX, True)

#? Update Presence_Penalty via Inline  
async def pres_penal_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = float(update['callback_query']['data'])
    
    #* Update Presence_Penalty
    return await Update_Command_Value (update, context, chat_id, new_val, 'presence_penalty', "⚠ Oops! Unexpected Error Occured. 😟", SEVEN)

#? Update Presence_Penalty via User Text Input 
async def pres_penal_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text

    #* Retrieve presence_penalty's range
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    available_options = my_data["OpenAICommands"]['presence_penalty'][1]
        
    new_val = float(new_val)    # raise error if text
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Presence_Penalty
        return await Update_Command_Value (update, context, chat_id, new_val, 'presence_penalty', "⚠ Oops! Unexpected Error Occured. 😟", SEVEN, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SEVEN, True)

#? Update Max_Length via Inline
async def max_len_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = int(update['callback_query']['data'])
    
    #* Update Max_Length
    return await Update_Command_Value (update, context, chat_id, new_val, 'max_length', "⚠ Oops! Unexpected Error Occured. 😟", THREE)

#? Update Max_Length via User Text Input 
async def max_len_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        #* Retrieve max_length's range
        with open('_Commands.json', 'r', encoding='utf-8') as f:
            my_data = json.load(f)
        available_options = my_data["OpenAICommands"]['max_length'][1]
        
        #! "text-davinci-003" the max_token is 4096, while for other models it is 2048
        curr_model = comd_val(chat_id, 'model')
        if (curr_model[0] == "text-davinci-003"): available_options[1] = 4096
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update Max_Length
            return await Update_Command_Value (update, context, chat_id, int(new_val), 'max_length', "⚠ Oops! Unexpected Error Occured. 😟", THREE, True)
        else:
            return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", THREE, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be Numeric!", THREE, True)

#? Update Best_Of via Inline
async def best_of_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = int(update['callback_query']['data'])
    
    #! best_of must be greater than n.
    n_curr_val = comd_val (chat_id, 'n')[0]
    if (int(new_val) < n_curr_val):
        return await comd_try_again(update, context, f"⚠ best_of must be greater than n ({n_curr_val})", EIGHT)

    #* Update Best_Of
    return await Update_Command_Value (update, context, chat_id, new_val, 'best_of', "⚠ Oops! Unexpected Error Occured. 😟", EIGHT)

#? Update Best_Of via User Text Input    
async def best_of_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        #* Retrieve max_length's range
        with open('_Commands.json', 'r', encoding='utf-8') as f:
            my_data = json.load(f)
        available_options = my_data["OpenAICommands"]['best_of'][1]
        
        #! best_of must be greater than n.
        n_curr_val = comd_val (chat_id, 'n')[0]
        if (int(new_val) < n_curr_val):
            return await comd_try_again(update, context, f"⚠ best_of must be greater than n ({n_curr_val})", EIGHT, True)
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update Best_Of
            return await Update_Command_Value (update, context, chat_id, int(new_val), 'best_of', "⚠ Oops! Unexpected Error Occured. 😟", EIGHT, True)
        else:
            return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", EIGHT, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be Numeric!", EIGHT, True)

#? Update N via Inline
async def n_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = int(update['callback_query']['data'])
    
    #! n must be smaller than best_of.
    b_curr_val = comd_val (chat_id, 'best_of')[0]
    if (int(new_val) > b_curr_val):
        return await comd_try_again(update, context, f"⚠ n must be smaller than best_of ({b_curr_val})", NINE)

    #* Update N
    return await Update_Command_Value (update, context, chat_id, new_val, 'n', "⚠ Oops! Unexpected Error Occured. 😟", NINE)

#? Update N via User Text Input
async def n_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        #* Retrieve n's range
        with open('_Commands.json', 'r', encoding='utf-8') as f:
            my_data = json.load(f)
        available_options = my_data["OpenAICommands"]['n'][1]
        
        #! n must be smaller than best_of.
        b_curr_val = comd_val (chat_id, 'best_of')[0]
        if (int(new_val) > b_curr_val):
            return await comd_try_again(update, context, f"⚠ n must be smaller than best_of ({b_curr_val})", NINE, True)
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update N
            return await Update_Command_Value (update, context, chat_id, int(new_val), 'n', "⚠ Oops! Unexpected Error Occured. 😟", NINE, True)
        else:
            return await comd_try_again(update, context, f"❗ Value must be between {available_options[0]} and {available_options[1]}", NINE, True)
    else:
        return await comd_try_again(update, context, f"❗ Value must be Numeric!", NINE, True)
    
#? Update Stop via User Text Input
async def stop_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    value = update.message.text
    new_val = [elem.strip() for elem in (value.split('\\\\'))]      # Split user's text by '\\'
    
    if (len(new_val) <= 4):
        #* Update Stop
        return await Update_Command_Value (update, context, chat_id, new_val, 'stop', "⚠ Oops! Unexpected Error Occured. 😟", FOUR, True)
    else:
        return await comd_try_again(update, context, "❗ Only upto 4 stop sequences are allowed!", FOUR, True)

#? Display User's Current Settings
async def CurrentSettings (update: Update, context: ContextTypes.DEFAULT_TYPE):
    import json
    chat_id = str(update.callback_query.from_user.id)
    filename = '_userSettings.json'
    with open(filename, "r") as file:
        data = json.load(file)
    message = ""
    for key in data[chat_id].keys():
        if (key=='num_openai_req'): break
        message = message + f"{key} : {data[chat_id][key]}\n"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("<b>Your Current Settings</b>\n\n" + message + "\n• Select <b>Change Settings</b> To Change\n• Select <b>Help</b> to know more", parse_mode='HTML')
    #* Show Main Menu
    return await BotOptionsCallApart (update, context)

#? Fall back to Default Settings
async def default (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    filename = '_userSettings.json'
    with open(filename, "r") as file:
        data = json.load(file)
    Backup_Data = data
    try:
        # Update to Default
        for key in OPENAI_KEYS:
            data[chat_id][key] = data["defualt_settings"][key]
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as err:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, str(err))
        with open(filename, "w") as f:                                  #! Incase any Error occurs, we don't lose our user data
            json.dump(Backup_Data, f, indent=4)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✅ Done! Setting changed to default!")
    #* Show Main Menu
    return await BotOptionsCallApart (update, context)

#? Display Setting's Info
async def commands (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'''
What Settings Do?

{COM_TXT[1]}

Try <b>Help</b> to know more!
'''
        , disable_web_page_preview=True
        , parse_mode='HTML'
)
    #* Show Settings Menu
    return await settings(update, context, True)

#? Display Contact Info
async def contact (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Hey there! 😊. It's wonderful to see you.\nConnect with me.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔸 ChatAI", url='https://chatai.typedream.app/')]])
    )
    #* Show Main Menu
    return await BotOptionsCallApart (update, context)

#? Error Handler  
async def error_han(update, context):
    """Log Errors caused by Updates."""
    chat_id = str(update.message.chat_id)
    logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, context.error)
    
##******************************************************* MAIN FUNCTION ******************************************************
def main():
    #! Bot API Key  -- using environment variable (from .env file) to avoid exposing the API key in the code
    BOT_TOKEN = config('TELE_BOT_API_KEY_2')

    #* By using Persistence, it is possible to keep inline buttons usable
    persistence = PicklePersistence(filepath='AysncChatAI_conv')
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    
    #* Send Anouncement to all users!
    # anouncement = False
    # if anouncement:
    #     bot.send_message(chat_id='<id>', text='We are up! 😀')
        
    load_commands_text()

    #* Handle Conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [
                CallbackQueryHandler(chat, pattern='^' + str(ONE) + '$'),                           # Start Text Generation
                CallbackQueryHandler(image, pattern='^' + str(TWO) + '$'),                          # Start Image Generation
                CallbackQueryHandler(help, pattern='^' + str(THREE) + '$'),                         # Show Help Message
                CallbackQueryHandler(settings, pattern='^' + str(FOUR) + '$'),                      # Settings Menu
                CallbackQueryHandler(CurrentSettings, pattern='^' + str(FIVE) + '$'),               # Show Current Settings Message
                CallbackQueryHandler(default, pattern='^' + str(SIX) + '$'),                        # Show Default Settings Message
                CallbackQueryHandler(commands, pattern='^' + str(SEVEN) + '$'),                     # Show Command (Get Info) Message
                CallbackQueryHandler(contact, pattern='^' + str(EIGHT) + '$')                       # Show Contact Screen
            ],
            CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat_intial),       # only messages and 'NOT'(~) commands
                CallbackQueryHandler(TerminateOpenAI, pattern='^' + str(CANCELOPT) + '$')           # Main Menu
            ],
            IMAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, image_intial),      #only messages and 'NOT'(~) commands
                CallbackQueryHandler(TerminateOpenAI, pattern='^' + str(CANCELOPT) + '$')           # Main Menu
            ],
            SETTINGS: [
                CallbackQueryHandler(model, pattern='^' + str(ONE) + '$'),                          # Model Screen
                CallbackQueryHandler(temperature, pattern='^' + str(TWO) + '$'),                    # Temperature Screen
                CallbackQueryHandler(max_length, pattern='^' + str(THREE) + '$'),                   # Max_Length Screen
                CallbackQueryHandler(stop, pattern='^' + str(FOUR) + '$'),                          # Stop Screen
                CallbackQueryHandler(top_p, pattern='^' + str(FIVE) + '$'),                         # Top_p Screen
                CallbackQueryHandler(frequency_penalty, pattern='^' + str(SIX) + '$'),              # Frequency Screen
                CallbackQueryHandler(presence_penalty, pattern='^' + str(SEVEN) + '$'),             # Presence Screen
                CallbackQueryHandler(best_of, pattern='^' + str(EIGHT) + '$'),                      # Best_of Screen
                CallbackQueryHandler(n, pattern='^' + str(NINE) + '$'),                             # N Screen
                CallbackQueryHandler(gen_probs, pattern='^' + str(TEN) + '$'),                      # Gen_Probs Screen
                CallbackQueryHandler(commands, pattern='^' + str(ELEVEN) + '$'),                    # Show Command (Get Info) Message
                CallbackQueryHandler(BotOptionsCallBack, pattern='^' + str(CANCELOPT) + '$'),       # Main Menu
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$')                # Settings Menu
            ],
            MODEL: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'),               # Settings Menu (this handler's presedence is imp.)
                CallbackQueryHandler(model_update),                                                 # This CallbackQueryHandler will handle any button pressed
                MessageHandler(filters.TEXT & ~filters.COMMAND, model_update_text)  # Any text input will be handled here
            ],
            TEMP: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'),
                CallbackQueryHandler(temp_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, temp_update_text)
            ],
            MAX_LENGTH: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'),
                CallbackQueryHandler(max_len_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, max_len_update_text)
            ],
            STOP: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, stop_update_text)
            ],
            TOP_P: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(top_p_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, top_p_update_text)
            ],
            FREQ_PENAL: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(freq_penal_update),
                MessageHandler(filters.TEXT & ~filters.COMMAND, freq_penal_update_text)
            ],
            PRES_PENAL: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(pres_penal_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, pres_penal_update_text)
            ],
            BEST_OF: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(best_of_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, best_of_update_text)
            ],
            N: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(n_update), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, n_update_text)
            ],
            GEN_PROBS: [
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'), 
                CallbackQueryHandler(gen_probs_update),
                MessageHandler(filters.TEXT & ~filters.COMMAND, gen_probs_update_text)
            ]
        },
        name="my_conversation",
        persistent=True,
        # run_async=True,
        fallbacks=[
            CommandHandler(['start', 'menu'], BotOptions),
            MessageHandler(filters.Text, BotOptions)
        ]
    )
    application.add_handler(conv_handler)
    
    #* Inline Query
    application.add_handler(InlineQueryHandler(inline_query_initial))
    
    #* Handle Errors
    application.add_error_handler(error_han)
    
    #* Open Bot to take commands
    application.run_polling()


if __name__ == '__main__':
    main()




# BOT_TOKEN = config('TELE_BOT_API_KEY_2')

# #* By using Persistence, it is possible to keep inline buttons usable
# persistence = PicklePersistence(filepath='AysncChatAI_conv')
# application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

# loop = asyncio.get_event_loop()

# async main():
    # await application.start()

    # await application.initialize()
    # bot = application.bot
    # dp = application.dispatcher
    #   code..............

# async def shutdown():
#     # Shut down the event loop
#     await application.shutdown()
#     await persistence.close()
#     await persistence.wait_closed()

# #* Start the Bot
# if __name__ == '__main__':
#     try:
#         # Start the main function
#         loop.run_until_complete(main())
#     except KeyboardInterrupt:
#         # Shut down the event loop on keyboard interrupt
#         loop.run_until_complete(shutdown())
#     finally:
#         # Close the event loop and clean up
#         loop.close()