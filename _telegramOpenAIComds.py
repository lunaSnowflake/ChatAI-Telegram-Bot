from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ForceReply
import json

from ChatAPI_req import *

#*::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#* Stages
MAIN, CHAT, CHAT_TRY_AGAIN, IMAGE, IMAGE_TRY_AGAIN, SETTINGS, MODEL, TEMP, MAX_LENGTH, STOP, TOP_P, FREQ_PENAL, PRES_PENAL, BEST_OF, N, GEN_PROBS, INIT_GROUP = range(17)
#* Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, ELEVEN = range(11)
#* Cancel Button (random big value is assigned -- MinInt)
from sys import maxsize
CANCELOPT = -(maxsize)
#*::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

async def keyboard_commands (update: Update, comd, text):
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    inline_keyboard = []
    available_options = my_data["OpenAICommands"][comd][1]
    available_options = list(zip(*[iter(available_options)]*2))
    for buttons in available_options:
        inline_keyboard.append(
            [
                InlineKeyboardButton(buttons[0], callback_data=buttons[0]),
                InlineKeyboardButton(buttons[1], callback_data=buttons[1])
            ]                 
        )
    inline_keyboard.append([InlineKeyboardButton("❌CANCEL", callback_data=str(CANCELOPT-1))])
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard))

async def model (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await keyboard_commands(update, 'model', "Select A Model.")
    return MODEL
    
async def gen_probs (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await keyboard_commands(update, 'gen_probs', "Enable Probilities?")
    return GEN_PROBS

async def input_commands_flt (update: Update, comd):
    with open('_Commands.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
    from numpy import linspace
    inline_keyboard = []
    raw_available_options = my_data["OpenAICommands"][comd][1]
    available_options = list(linspace(raw_available_options[0],raw_available_options[1],4))
    available_options = [ '%.1f' % elem for elem in available_options ]
    available_options = list(zip(*[iter(available_options)]*2))
    for buttons in available_options:
        inline_keyboard.append(
            [
                InlineKeyboardButton(buttons[0], callback_data=float(buttons[0])),
                InlineKeyboardButton(buttons[1], callback_data=float(buttons[1]))
            ]
        )
    inline_keyboard.append([InlineKeyboardButton("❌CANCEL", callback_data=str(CANCELOPT-1))])
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"• Select <b>{comd}</b> from one of the Options available.\n• Or send a value between {raw_available_options[0]} and {raw_available_options[1]}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
        parse_mode= 'HTML'
    )

async def temperature (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await input_commands_flt (update, 'temperature')
    return TEMP

async def top_p (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await input_commands_flt (update, 'top_p')
    return TOP_P

async def frequency_penalty (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await input_commands_flt (update, 'frequency_penalty')
    return FREQ_PENAL

async def presence_penalty (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await input_commands_flt (update, 'presence_penalty')
    return PRES_PENAL

async def input_commands_int (update: Update, raw_available_options, comd):
    from numpy import linspace
    inline_keyboard = []
    available_options = list(linspace(raw_available_options[0],raw_available_options[1],6))
    available_options = [ int(elem) for elem in available_options ]
    available_options = list(zip(*[iter(available_options)]*3))
    for buttons in available_options:
        inline_keyboard.append(
            [
                InlineKeyboardButton(buttons[0], callback_data=int(buttons[0])),
                InlineKeyboardButton(buttons[1], callback_data=int(buttons[1])),
                InlineKeyboardButton(buttons[2], callback_data=int(buttons[2]))
            ]                 
        )
    inline_keyboard.append([InlineKeyboardButton("❌CANCEL", callback_data=str(CANCELOPT-1))])
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"• Select <b>{comd}</b> from one of the Options available.\n• Or send a value between {raw_available_options[0]} and {raw_available_options[1]}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
        parse_mode= 'HTML'
    )
    
async def max_length (update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.callback_query.from_user.id)
    available_options = [1, 2048]
    
    #? "text-davinci-003" the max_token is 4096, while for other models it is 2048
    curr_model = json.loads(await get_user_setting_api(chat_id, sett='model')).get('settings')
    if (curr_model == "text-davinci-003"): available_options[1] = 4096
    
    await input_commands_int (update, available_options, 'max_length')
    
    return MAX_LENGTH

async def best_of (update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_options = [1,20]
    await input_commands_int (update, available_options, 'best_of')
    return BEST_OF

async def n (update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_options = [1,20] 
    await input_commands_int (update, available_options, 'n')    
    return N

async def stop (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text('Up to 4 sequences are allowed')
    await update.callback_query.message.reply_text(
        'Seperate your sequences with \"\\\\\"',
        reply_markup=ForceReply(input_field_placeholder='A \\\\ B \\\\ C \\\\ D')
    )
    inline_keyboard = [[InlineKeyboardButton("❌CANCEL", callback_data=str(CANCELOPT-1))]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.callback_query.message.reply_text("Cancel", reply_markup=inline_markup)
    return STOP



