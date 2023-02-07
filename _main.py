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
import os
import html
import traceback

from telegram import Chat
from telegram.ext import ChatMemberHandler
from group_handler_bot import update_chat_members, group_update, send_group_intro

from _telegramOpenAIComds import *
from _reqOpenAI import send_req_openai_chat, send_req_openai_image
from _BotInlineQuery import inline_query_initial

# Enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(module)s - %(funcName)s - ln %(lineno)d - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

#! Bot API Key  -- using environment variable (from .env file) to avoid exposing the API key in the code
from decouple import config
BOT_TOKEN = config('TELE_BOT_API_KEY_3')
# BOT_TOKEN = config('TELE_BOT_API_KEY_2') #ChatAI
bot = Bot(BOT_TOKEN)

#* Global Variables
COM_TXT = []

#? Load The Command text that will used later by /help, /commands, etc
def load_commands_text():
    global COM_TXT
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
        MainComm = my_data.keys()
        for Mkey in MainComm: 
            Comm = my_data[Mkey].keys()
            text = ''
            for key in Comm:
                if key == "echo": continue
                text = text + '• ' + '<b>' + key.title() + '</b>' + ' - ' + my_data[Mkey][key][0] + '\n'
            COM_TXT.append(text)

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
        InlineKeyboardButton("❤ Feedback", url='https://bit.ly/ChatAIform')
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
async def BotOptions (update: Update, context: ContextTypes.DEFAULT_TYPE, text="Choose What You Would Like To Do? 😀"):
    #* PROMPT
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(Main_Menu_Buttons))
    #* Un-pin all messages from chat
    chat_id = str(update.message.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN

#? When Setting Canceled is pressed -- Callback
async def BotOptionsCallBack (update: Update, context: ContextTypes.DEFAULT_TYPE, text="Choose What You Would Like To Do? 😀"):
    #* PROMPT
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(Main_Menu_Buttons))
    #* Un-pin all messages from chat
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN

#? Generate in separate message -- Callback
async def BotOptionsCallApart (update: Update, text="Choose What You Would Like To Do? 😀"):
    #* PROMPT
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(Main_Menu_Buttons))
    #* Un-pin all messages from chat
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN

#? Add To User Info to Database (if new-user)
async def new_user (update: Update, is_group=False):
    chat_id = str(update.message.from_user.id)
    statusCode = await new_user_api(update, chat_id)
    
    #* Add New User
    isnewlyadded = False
    if statusCode == 201:               # User Added
        isnewlyadded = True
    elif statusCode == 409:             # User Already Exist
        if is_group: return
        isnewlyadded = False
    else:                               # Other Errors
        return False
    
    if isnewlyadded:
        logger.info(f"Starting Bot for {chat_id}")
        await update.message.reply_text(f"Welcome {update.message.from_user.first_name}! 😀")
        #* Add Defualt setting for new User
        statusCode = await new_setting_api(chat_id)
        if statusCode == 201:           # User Setting Added
            return True
        else:
            return False
    else:
        logger.info(f"Re-starting Bot for {chat_id}")
        await update.message.reply_text(f"Welcome Back {update.message.from_user.first_name}! 😀")
    
    return True
  
#? Start
async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Only allow Conversation Handler in Private Chat
    chat = update.effective_chat
    if chat.type != Chat.PRIVATE:
        await send_group_intro(update)
        return ConversationHandler.END
    
    #* Add New User
    status = await new_user(update)
    
    #* Prompt to User
    if status:
        await update.message.reply_text(f'''
Hello!, Welcome to <a href='https://chatai.typedream.app/'>ChatAI</a> 😊
I can help you with :
• Text Completion 🗨️
• Image Generation 🎴
This Bot is based on <a href='https://bit.ly/OpenAI_Introduction'>OpenAI</a>
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
<a href='https://chatai.typedream.app/'>ChatAI</a> is a Telegram Bot that can help you with:
• Text Completion (ChatGPT3)
• Image Generation (Dall-E 2)

• <b>Text Generation :</b> Start Text Completion!
• <b>Image Generation :</b> Start Image Generation!
• <b>Change Settings :</b> Alter Your Settings For Text Completion!
• <b>Current Settings :</b> Check Your Settings For Text Completion!
• <b>Default Settings :</b> Fall Back To Default Settings!
• <b>Command Info :</b> Learn About Different Settings!

More more info visit our page <a href='https://chatai.typedream.app/'>ChatAI</a>
'''
        , disable_web_page_preview=True
        , parse_mode='HTML'
    )
    #* Show Main Menu
    return await BotOptionsCallApart (update)

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
    await update.callback_query.message.reply_text("• Try writting something like:\n<b>\"Write a tagline for an ice cream shop.\"</b>", disable_web_page_preview=True, parse_mode='HTML', reply_markup=reply_markup)
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
    await update.callback_query.message.reply_text("• Try writting something like:\n<b>\"A cute chow chow dog with birthday hat.\"</b>", disable_web_page_preview=True, parse_mode='HTML', reply_markup=reply_markup)
    #* Tell ConversationHandler that we're in state `IMAGE` now
    return IMAGE

#? Chat Intialize
async def chat_intial (update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await openai_handler (update, context, type=0)
#? Image Intialize
async def image_intial (update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await openai_handler (update, context, type=1)

#? OpenAI Handler
async def openai_handler (update: Update, context: ContextTypes.DEFAULT_TYPE, type=0):
    #* Prompt "Generate..." Message to User
    gen_msg = await update.message.reply_text("Generating...", reply_markup=ReplyKeyboardRemove())
    #* Generate
    text = update.message.text
    chat_id = str(update.message.from_user.id)
    try:
        #* Send Chat OpenAI request
        if (type==0):
            try:
                logger.info(f"Requesting OpenAI TextCompletion: {chat_id}")
                response, prob_file, num_openai_req = await send_req_openai_chat(update, text, chat_id, False)
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
                    os.remove(prob_file)        # Delete Probability File
                #* If user's first query of the day, give a Tip to change settings
                # num_openai_req = int(json.loads(await get_user_setting_api (chat_id, sett='num_openai_req')).get('settings'))
                if num_openai_req == 1:
                    await update.message.reply_text("💡Tips:\n• You can change settings for Text Generation using 'Change Settings' from Main Menu.\n• Use '🏠 Main Menu' from above pinned to go back.")
        #* Send Image OpenAI request
        else:
            #* The maximum length is 1000 characters. (950 for buffer)
            if (len(text)>950):
                await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)          # Delete "Generating..." message
                await update.message.reply_text("❗ Query too long (The maximum length is 1000 characters.)")
            else:
                try:
                    logger.info(f"Requesting OpenAI Image Generation: {chat_id}")
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
    #* Prompt Terminate Message to User and **Remove any Reply-Keyboard**
    await update.callback_query.answer()
    # gen_msg = await update.callback_query.message.reply_text("🏠 Going Back Home..😊", reply_markup=ReplyKeyboardRemove())
    #* Un-pin all messages from chat -- the cancel message
    chat_id = str(update.callback_query.from_user.id)
    await bot.unpin_all_chat_messages(chat_id=chat_id)
    #* Delete Generated Message
    # await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)
    #* Show Main Menu
    inline_markup = InlineKeyboardMarkup(Main_Menu_Buttons)
    await update.callback_query.message.reply_text("What would you like to do? 😀", reply_markup=inline_markup)
    #* Tell ConversationHandler that we're in state `MAIN` now
    return MAIN
    
#? Settings
async def settings (update: Update, context: ContextTypes.DEFAULT_TYPE, msg="", isText=False):
    #* Prompt Settings Menu to User
    inline_markup = InlineKeyboardMarkup(Settings_Buttons)
    if msg == "":
        msg = '''
Select the setting, you want to Change.
ℹ <b>Remember:</b> It'll affect your Text Completion.
Use <b>Get Info</b> to learn more.
'''
    else:
        msg = msg + "\nWhat next?"
        
    if (not isText):            # When called from Callback -- replace previous prompt
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg, reply_markup=inline_markup, parse_mode="HTML")
    else:                       # When called from _text() functions
        try:
            await update.message.reply_text(msg, reply_markup=inline_markup, parse_mode="HTML")
        except:                 # When called from Callback -- make new prompt
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(msg, reply_markup=inline_markup, parse_mode="HTML")
    #* Tell ConversationHandler that we're in state `SETTINGS` now
    return SETTINGS

#? Error occured while making change in Settings
async def comd_try_again (update: Update, text, callback_val, isText=False):
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
async def Update_Command_Value (update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, new_val, comd, callback_val, isText=False):
    #* Update user's settings
    setts = {comd: new_val}                                      #******** Update comd's value **********
    statusCode = await update_setting_api(chat_id, setts)
    
    if statusCode == 201:        
        if (not isText):            # When called from Callback -- replace previous prompt
            await update.callback_query.answer()
            # await update.callback_query.edit_message_text(text = f"✅ Done! {comd} changed to: {new_val}")
            return await settings (update, context, msg=f"✅ Done! <b>{comd}</b> changed to: {new_val}")           # Call settings and show Settings Menu
        else:                       # When called from _text() functions
            # await update.message.reply_text(text = f"✅ Done! {comd} changed to: {new_val}")
            return await settings (update, context, msg=f"✅ Done! <b>{comd}</b> changed to: {new_val}", isText=True)     # Call settings and show Settings Menu
    else:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, "setting could not be updated")
        return await comd_try_again(update, "⚠ Oops! Unexpected Error Occured. 😟", callback_val, isText)

#? Update Model via Inline 
async def model_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']

    #? "text-davinci-003" the max_token is 4096, while for other models it is 2048
    if (new_val != "text-davinci-003"):
        curr_max_length = int(json.loads(await get_user_setting_api(chat_id, sett='max_length')).get('settings'))
        if (curr_max_length > 2048):
            setts = {"max_length": "2048"}
            statusCode = await update_setting_api(chat_id, setts)
            if statusCode != 201:
                logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, "During model updation max_length could not be updated")
                return await comd_try_again(update, "⚠ Oops! Unexpected Error Occured. 😟", ONE)

    #* Update Model
    return await Update_Command_Value (update, context, chat_id, new_val, 'model', "⚠ Oops! Unexpected Error Occured. 😟", ONE)

#? When Model via User Text Input
async def model_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #*Try Again when any text is entered for Model
    return await comd_try_again(update, '❗ Choose from Options', ONE, True)

#? Update Gen_Probs via Inline
async def gen_probs_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = True if (update['callback_query']['data']=="True") else False
    
    #* Update Gen_Probs
    return await Update_Command_Value (update, context, chat_id, new_val, 'gen_probs', TEN)

#? When Gen_Probs via User Text Input
async def gen_probs_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #*Try Again when any text is entered for Gen_Probs
    return await comd_try_again(update, '❗ Choose from Options', TEN, True)

#? Update Temperature via Inline
async def temp_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #* Update Temperature
    return await Update_Command_Value (update, context, chat_id, new_val, 'temperature', TWO)

#? Update Temperature via User Text Input      
async def temp_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text

    available_options = [0,1]
    try:
        new_val = float(new_val)    # raise error if text
    except:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", TWO, True)
    
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Temperature
        return await Update_Command_Value (update, context, chat_id, str(new_val), 'temperature', TWO, isText=True)
    else:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", TWO, True)

#? Update Top_P via Inline
async def top_p_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #* Update Top_P
    return await Update_Command_Value (update, context, chat_id, new_val, 'top_p', FIVE)

#? Update Top_P via User Text Input
async def top_p_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text

    available_options = [0,1]
    try:
        new_val = float(new_val)    # raise error if text
    except:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", FIVE, True)
        
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Top_P
        return await Update_Command_Value (update, context, chat_id, str(new_val), 'top_p', FIVE, isText=True)
    else:
        return await comd_try_again (update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", FIVE, True)

#? Update Frequency_Penalty via Inline
async def freq_penal_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #* Update Frequency_Penalty
    return await Update_Command_Value (update, context, chat_id, new_val, 'frequency_penalty', SIX)

#? Update Frequency_Penalty via User Text Input   
async def freq_penal_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text

    available_options = [-2,2]        
    try:
        new_val = float(new_val)    # raise error if text
    except:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SIX, True)
        
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Frequency_Penalty
        return await Update_Command_Value (update, context, chat_id, str(new_val), 'frequency_penalty', SIX, isText=True)
    else:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SIX, True)

#? Update Presence_Penalty via Inline  
async def pres_penal_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #* Update Presence_Penalty
    return await Update_Command_Value (update, context, chat_id, new_val, 'presence_penalty', SEVEN)

#? Update Presence_Penalty via User Text Input 
async def pres_penal_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text

    available_options = [-2,2]
    try:
        new_val = float(new_val)    # raise error if text
    except:
        return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SEVEN, True)
        
    if (available_options[0] <= new_val <= available_options[1]):
        #* Update Presence_Penalty
        return await Update_Command_Value (update, context, chat_id, str(new_val), 'presence_penalty', SEVEN, isText=True)
    else:
        return await comd_try_again (update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", SEVEN, True)

#? Update Max_Length via Inline
async def max_len_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #* Update Max_Length
    return await Update_Command_Value (update, context, chat_id, new_val, 'max_length', THREE)

#? Update Max_Length via User Text Input 
async def max_len_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        available_options = [1, 2048]
        
        #! "text-davinci-003" the max_token is 4096, while for other models it is 2048
        curr_model = int(json.loads(await get_user_setting_api(chat_id, sett='max_length')).get('settings'))
        if (curr_model == "text-davinci-003"): available_options[1] = 4096
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update Max_Length
            return await Update_Command_Value (update, context, chat_id, str(new_val), 'max_length', THREE, isText=True)
        else:
            return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", THREE, True)
    else:
        return await comd_try_again(update, f"❗ Value must be Numeric!", THREE, True)
    
#? Update Best_Of via Inline
async def best_of_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #! best_of must be greater than n.
    n_curr_val = int(json.loads(await get_user_setting_api(chat_id, sett='n')).get('settings'))
    if (int(new_val) < n_curr_val):
        return await comd_try_again(update, f"⚠ best_of must be greater than n ({n_curr_val})", EIGHT)

    #* Update Best_Of
    return await Update_Command_Value (update, context, chat_id, new_val, 'best_of', EIGHT)

#? Update Best_Of via User Text Input    
async def best_of_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        available_options = [1,20]
        
        #! best_of must be greater than n.
        n_curr_val = int(json.loads(await get_user_setting_api(chat_id, sett='n')).get('settings'))
        if (int(new_val) < n_curr_val):
            return await comd_try_again(update, f"⚠ best_of must be greater than n ({n_curr_val})", EIGHT, True)
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update Best_Of
            return await Update_Command_Value (update, context, chat_id, str(new_val), 'best_of', EIGHT, isText=True)
        else:
            return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", EIGHT, True)
    else:
        return await comd_try_again(update, f"❗ Value must be Numeric!", EIGHT, True)
    
#? Update N via Inline
async def n_update (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    new_val = update['callback_query']['data']
    
    #! n must be smaller than best_of.
    b_curr_val = int(json.loads(await get_user_setting_api(chat_id, sett='best_of')).get('settings'))
    if (int(new_val) > b_curr_val):
        return await comd_try_again(update, f"⚠ n must be smaller than best_of ({b_curr_val})", NINE)

    #* Update N
    return await Update_Command_Value (update, context, chat_id, new_val, 'n', NINE)

#? Update N via User Text Input
async def n_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    new_val = update.message.text
    
    #* Check User's Value is Numeric (Not Float or Text)
    if new_val.isnumeric():
        available_options = [1,20]
        
        #! n must be smaller than best_of.
        b_curr_val = int(json.loads(await get_user_setting_api(chat_id, sett='best_of')).get('settings'))
        if (int(new_val) > b_curr_val):
            return await comd_try_again(update, f"⚠ n must be smaller than best_of ({b_curr_val})", NINE, True)
        
        if (available_options[0] <= int(new_val) <= available_options[1]):
            #* Update N
            return await Update_Command_Value (update, context, chat_id, str(new_val), 'n', NINE, isText=True)
        else:
            return await comd_try_again(update, f"❗ Value must be between {available_options[0]} and {available_options[1]}", NINE, True)
    else:
        return await comd_try_again(update, f"❗ Value must be Numeric!", NINE, True)
    
#? Update Stop via User Text Input
async def stop_update_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.from_user.id)
    value = update.message.text
    new_val = [elem.strip() for elem in (value.split('\\\\'))]      # Split user's text by '\\'
    
    if (len(new_val) <= 4):
        #* Update Stop
        return await Update_Command_Value (update, context, chat_id, str(new_val), 'stop', FOUR, isText=True)
    else:
        return await comd_try_again(update, "❗ Only upto 4 stop sequences are allowed!", FOUR, True)

#? Display User's Current Settings
async def CurrentSettings (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    data = json.loads(await get_user_setting_api(chat_id)).get('settings')
    message = ""
    for key in data.keys():
        if (key=='num_openai_req' or key=='last_openai_req' or key=='total_queries' or key=='chat_id' or key=='echo'): continue
        message = message + f"• <b>{key} : </b>{data[key]}\n"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("<b>Commands for Text Completion</b>\n\n" + message + "\nSelect <b>Change Settings</b> to change.\nSelect <b>Help</b> to know more.", parse_mode='HTML')
    #* Show Main Menu
    return await BotOptionsCallApart (update)

#? Fall back to Default Settings
async def default (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    statusCode = await update_setting_api(chat_id)
    msg = "✅ Done! Setting changed to default!"
    if statusCode != 201:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, "Error while falling back to defualt settings")
        msg = "⚠ Oops! Something went wrong, please try again"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(msg)
    #* Show Main Menu
    return await BotOptionsCallApart (update)

#? Display Setting's Info
async def commands (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f'''
What Settings Do?
ℹ Remember it will affect your Text Completion.

{COM_TXT[1]}
Select <b>Help</b> to know more.
'''
        , disable_web_page_preview=True
        , parse_mode='HTML'
)
    #* Show Settings Menu
    return await settings (update, context, isText=True)

#? Display Contact Info
async def contact (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"Hey there! 😊. It's wonderful to see you.\nConnect with me.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔸 ChatAI", url='https://chatai.typedream.app/')]])
    )
    #* Show Main Menu
    return await BotOptionsCallApart (update)

#? Error Handler  
async def error_han(update, context):
    """Log Errors caused by Updates."""
    try:
        chat_id = str(update.message.from_user.id)
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', chat_id, context.error)
        #* Send developer that retry was successful
        context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text="!!Done Retrying Error!!", parse_mode="HTML")
        #* show menu to user
        try:
            return await BotOptions (update, context, "Oops something went wrong!🤔\nPlease try again!\nUse /menu")
        except:
            return await BotOptionsCallApart (update, "Oops something went wrong!🤔\nPlease try again!\nUse /menu")
    except:
        logger.warning('UPDATE: "%s" \nCAUSED ERROR: "%s"', '<no chat_id>', context.error)
    try:
        #* Send Error Message to Developer. -- or send through Telegram Group 'ChatAI Log'(chat_id: "-632198831").
        DEVELOPER_CHAT_ID = config('ADMIN_TELE_ID')
        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        # Build the message with some markup and additional information about what happened.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        # Finally, send the message (telegram has a message limit of 4096 characters).
        await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message[:4096], parse_mode="HTML")
    except: pass
        
async def group_req_text (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Only Group chats are allowed to use this commands
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE: return ConversationHandler.END
    
    chat_id = str(update.message.chat_id)       # or group_id
    user_id = str(update.message.from_user.id)
    
    #* Add as a new user (if user already in the database nothing will change)
    status = await new_user(update, is_group=True)
    
    #* Send Response
    logger.info(f"Requesting OpenAI TextCompletion: In group:{chat_id}:{user_id}")
    gen_msg = await update.message.reply_text("Generating...")
        
    text = update.message.text.partition(' ')[2]       # Input provided next to the command
            
    response, prob_file, num_openai_req = await send_req_openai_chat(update, text, user_id, True)
    await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)
    
    await update.message.reply_text(
        text = response,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )
    
async def group_req_img (update: Update, context: ContextTypes.DEFAULT_TYPE):
    #* Only Group chats are allowed to use this commands
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE: return ConversationHandler.END
    
    chat_id = str(update.message.chat_id)       # or group_id
    user_id = str(update.message.from_user.id)
    
    #* Add as a new user (if user already in the database nothing will change)
    status = await new_user(update, is_group=True)
    
    #* Send Response
    logger.info(f"Requesting OpenAI Image Generation: In group:{chat_id}:{user_id}")
    gen_msg = await update.message.reply_text("Generating...")
        
    text = update.message.text.partition(' ')[2]       # Input provided next to the command
    
    response, limit = await send_req_openai_image(update, text, user_id, True)
    await bot.delete_message(chat_id=gen_msg.chat_id, message_id=gen_msg.message_id)
    
    if (not limit): await update.message.reply_photo(photo=response)
    else: await update.message.reply_text(response)
    
##******************************************************* MAIN FUNCTION ******************************************************
def main():
    #* By using Persistence, it is possible to keep inline buttons usable
    #* The telegram will store all the data in the "context", but this data will be erased if bot is stopped. 
    #* To avoid losing the data, we can store the data in a file using PicklePersistence.
    persistence = PicklePersistence(filepath='ChatAI_conversation')
    application = Application.builder().token(BOT_TOKEN).concurrent_updates(True).persistence(persistence).build()
    
    #* When bot is started
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
                # CallbackQueryHandler(contact, pattern='^' + str(EIGHT) + '$')                       # Show Contact Screen
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
                CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$'),               # Settings Menu (the handler's presedence is imp.)
                CallbackQueryHandler(model_update),                                                 # This CallbackQueryHandler will handle any button pressed
                MessageHandler(filters.TEXT & ~filters.COMMAND, model_update_text)                  # Any text input will be handled here
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
            MessageHandler(filters.TEXT & ~filters.COMMAND, BotOptions)
        ]
    )
    application.add_handler(conv_handler)
    
    #* ChatAI Added to Group Update
    application.add_handler(ChatMemberHandler(group_update, ChatMemberHandler.MY_CHAT_MEMBER))
    #* Group Commands
    application.add_handler(CommandHandler('text', group_req_text))
    application.add_handler(CommandHandler('img', group_req_img))
    
    #* Inline Query
    application.add_handler(InlineQueryHandler(inline_query_initial))
    
    #* Handle Errors
    # application.add_error_handler(error_han)
    
    #* Open Bot to take commands
    # try:
    #     ''' If want to Delete Webhook connection manually: https://api.telegram.org/bot5983430779:AAE3UIeIXCooM0bOL0BBKOLuC_qkcVxdchs/deleteWebhook 
    #         If using python-telegram-bot v20.x to use webhook install: pip install python-telegram-bot[webhooks]'''
    #     #* WebHook: using ngrok's tunneling: https://dashboard.ngrok.com/tunnels/agents)
    #     '''We are running this on our system port 'Localhost:8443' which using ngrok we are tunneling so that open internet could access. 
    #         Hence Telegram will send request to ngrok which in result send it to our port which we are listing to.
    #         To get ngrok url: Open cmd and goto the location where file "ngrol.exe" is located. Then type "ngrok http 8443"'''
    #     webhook_url = config('NGROK_URL') + '/' + BOT_TOKEN
    #     logger.info(f"Using webhooks - running on: {webhook_url}")
    #     #* WebHook: AWS API Gateway and Lambda Function 
    #     ''' Working but don't know how to implement yet😔. 
    #         To make it work we need to setup SSH server using OpenSSH'''
    #     # webhook_url = config('AWS_URL')
    #     # logger.info("Using webhooks. - running on: AWS Api")
    #     PORT = int(os.environ.get('PORT', 8443))
    #     application.run_webhook(
    #         listen="0.0.0.0",
    #         port=PORT,
    #         url_path=BOT_TOKEN,             
    #         webhook_url = webhook_url
    #     )
    # except Exception as err:
    #* Polling
    logger.info("Using polling") #, due to Error: ", err)
    application.run_polling()

#* Start the Bot
if __name__ == '__main__':
    main()





# #* By using Persistence, it is possible to keep inline buttons usable even after the bot got shutdown as it stores the DATA FOR EACH USER
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


#* Concurrency on each Handler level -- block=False
#*
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #     states={
    #         MAIN: [
    #             CallbackQueryHandler(chat, pattern='^' + str(ONE) + '$', block=False),                           # Start Text Generation
    #             CallbackQueryHandler(image, pattern='^' + str(TWO) + '$', block=False),                          # Start Image Generation
    #             CallbackQueryHandler(help, pattern='^' + str(THREE) + '$', block=False),                         # Show Help Message
    #             CallbackQueryHandler(settings, pattern='^' + str(FOUR) + '$', block=False),                      # Settings Menu
    #             CallbackQueryHandler(CurrentSettings, pattern='^' + str(FIVE) + '$', block=False),               # Show Current Settings Message
    #             CallbackQueryHandler(default, pattern='^' + str(SIX) + '$', block=False),                        # Show Default Settings Message
    #             CallbackQueryHandler(commands, pattern='^' + str(SEVEN) + '$', block=False),                     # Show Command (Get Info) Message
    #             # CallbackQueryHandler(contact, pattern='^' + str(EIGHT) + '$', block=False)                       # Show Contact Screen
    #         ],
    #         CHAT: [
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, chat_intial, block=False),       # only messages and 'NOT'(~) commands
    #             CallbackQueryHandler(TerminateOpenAI, pattern='^' + str(CANCELOPT) + '$', block=False)           # Main Menu
    #         ],
    #         IMAGE: [
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, image_intial, block=False),      #only messages and 'NOT'(~) commands
    #             CallbackQueryHandler(TerminateOpenAI, pattern='^' + str(CANCELOPT) + '$', block=False)           # Main Menu
    #         ],
    #         SETTINGS: [
    #             CallbackQueryHandler(model, pattern='^' + str(ONE) + '$', block=False),                          # Model Screen
    #             CallbackQueryHandler(temperature, pattern='^' + str(TWO) + '$', block=False),                    # Temperature Screen
    #             CallbackQueryHandler(max_length, pattern='^' + str(THREE) + '$', block=False),                   # Max_Length Screen
    #             CallbackQueryHandler(stop, pattern='^' + str(FOUR) + '$', block=False),                          # Stop Screen
    #             CallbackQueryHandler(top_p, pattern='^' + str(FIVE) + '$', block=False),                         # Top_p Screen
    #             CallbackQueryHandler(frequency_penalty, pattern='^' + str(SIX) + '$', block=False),              # Frequency Screen
    #             CallbackQueryHandler(presence_penalty, pattern='^' + str(SEVEN) + '$', block=False),             # Presence Screen
    #             CallbackQueryHandler(best_of, pattern='^' + str(EIGHT) + '$', block=False),                      # Best_of Screen
    #             CallbackQueryHandler(n, pattern='^' + str(NINE) + '$', block=False),                             # N Screen
    #             CallbackQueryHandler(gen_probs, pattern='^' + str(TEN) + '$', block=False),                      # Gen_Probs Screen
    #             CallbackQueryHandler(commands, pattern='^' + str(ELEVEN) + '$', block=False),                    # Show Command (Get Info) Message
    #             CallbackQueryHandler(BotOptionsCallBack, pattern='^' + str(CANCELOPT) + '$', block=False),       # Main Menu
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False)                # Settings Menu
    #         ],
    #         MODEL: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False),               # Settings Menu (the handler's presedence is imp.)
    #             CallbackQueryHandler(model_update, block=False),                                                 # This CallbackQueryHandler will handle any button pressed
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, model_update_text, block=False)                  # Any text input will be handled here
    #         ],
    #         TEMP: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False),
    #             CallbackQueryHandler(temp_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, temp_update_text, block=False)
    #         ],
    #         MAX_LENGTH: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False),
    #             CallbackQueryHandler(max_len_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, max_len_update_text, block=False)
    #         ],
    #         STOP: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False),
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, stop_update_text, block=False)
    #         ],
    #         TOP_P: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(top_p_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, top_p_update_text, block=False)
    #         ],
    #         FREQ_PENAL: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(freq_penal_update, block=False),
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, freq_penal_update_text, block=False)
    #         ],
    #         PRES_PENAL: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(pres_penal_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, pres_penal_update_text, block=False)
    #         ],
    #         BEST_OF: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(best_of_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, best_of_update_text, block=False)
    #         ],
    #         N: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(n_update, block=False), 
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, n_update_text, block=False)
    #         ],
    #         GEN_PROBS: [
    #             CallbackQueryHandler(settings, pattern='^' + str(CANCELOPT-1) + '$', block=False), 
    #             CallbackQueryHandler(gen_probs_update, block=False),
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, gen_probs_update_text, block=False)
    #         ]
    #     },
    #     name="my_conversation",
    #     persistent=True,
    #     # run_async=True,
    #     fallbacks=[
    #         CommandHandler(['start', 'menu'], BotOptions, block=False),
    #         MessageHandler(filters.Text, BotOptions, block=False)
    #     ]
    # )
    # application.add_handler(conv_handler)
    
    # #* Inline Query
    # application.add_handler(InlineQueryHandler(inline_query_initial, block=False))