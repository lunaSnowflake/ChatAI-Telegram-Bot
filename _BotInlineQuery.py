
#********************************Inline Query (This will run when user type: @botusername <query>)****************************************************
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto #, InlineQueryResultDocument

from _reqOpenAI import *

#? Inline Query Handler
from uuid import uuid4
async def inline_query_initial(update: Update, context: ContextTypes.DEFAULT_TYPE):         #? inline_query_initial -- with end of the query model ("\\")
    query = update.inline_query.query
    if query != "":
        query = query.strip()
        if query.endswith('\\\\'):
            if (len(query) <= 230):         # This is the no. of characters that user can write in inline query
                if query.startswith('i-'):
                    # update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Generating!🔄, Please wait.....",input_message_content=InputTextMessageContent("Not Valid!"))])
                    await inline_query_image(update, query.lstrip("i-").rstrip(('\\\\')))
                else:
                    # update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Generating!🔄, Please wait.....",input_message_content=InputTextMessageContent("Not Valid!"))])
                    await inline_query_text(update, query.rstrip("\\\\"))
            else:
                await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description=f"⚠ Query must not exceed 230 characters.",input_message_content=InputTextMessageContent("Invalid Input!"))])
        else:
            await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Put \'\\\\\' at the end to start Generarting.",input_message_content=InputTextMessageContent("Invalid Input!"))])
    else:
        await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="💡Start writing to Generate.\n• End your query with \'\\\\\'\n• For Image generation, use 'i-' flag at start.",input_message_content=InputTextMessageContent("Invalid Input!"))])

#* This code is Efficient to provide Real Time "Text Completion", 
#* though becuase to avoid unnessary (tons) of OpenAI API requests, 
#* and also as it produces high amount of machine load (which if not be handled correctly by the machine, it can produce unexpected results), 
#* hence to avoid this we made a wrapper function inline_query_initial(), 
#* which will allow this function to run only if the user put '\\' at the end of its query.
async def inline_query_text(update: Update, query) -> None:
    #* Send OpenAI Request
    chat_id = str(update.inline_query.from_user.id)
    
    try:
        response, prob_file = await send_req_openai_chat(update, query, chat_id, True)
        results = [
            InlineQueryResultArticle(                                       #* https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py
                id = str(uuid4()),
                title = "ChatAI",
                description = query[:50],
                input_message_content = InputTextMessageContent(response)
                # reply_markup = InlineKeyboardMarkup(inline_keyboard)          # You can generate an inline keyboard too
            )
        ]
    except:
        results = [
            InlineQueryResultArticle(
                id = str(uuid4()),
                title = "ChatAI",
                description = "⚠ OOPS! ERROR OCCURED.",
                input_message_content = InputTextMessageContent("⚠ Oops! Error Occured.😶\nTry again!")
            )
        ]
    #* Display Pop-up
    await update.inline_query.answer(results=results)

async def inline_query_image (update: Update, query) -> None:
    #* Send OpenAI Request
    chat_id = str(update.inline_query.from_user.id)

    try:
        response, limit = await send_req_openai_image(update, query, chat_id, True)
        if (not limit):
            results = [
                InlineQueryResultPhoto(                                       #* https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py
                    id = str(uuid4()),
                    title = "ChatAI",
                    description = query[:50],
                    photo_url = response,
                    thumb_url = response
                )
            ]
        else:
            results = [
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title = "ChatAI",
                    description = "⚠ YOUR MAX LIMIT EXHUASTED!",
                    input_message_content = InputTextMessageContent("⚠ Your Max Limit Exhuasted!\nTry again Tommorrow")
                )
            ]
    except:
        results = [
            InlineQueryResultArticle(
                id = str(uuid4()),
                title = "ChatAI",
                description = "⚠ OOPS! ERROR OCCURED.",
                input_message_content = InputTextMessageContent("⚠ Oops! Error Occured.😶\nTry again!")
            )
        ]
    #* Display Pop-up
    await update.inline_query.answer(results=results)