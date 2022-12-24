
#********************************Inline Query (This will run when user type: @botusername <query>)****************************************************
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineQueryResultArticle, InputTextMessageContent #, InlineQueryResultDocument, InlineQueryResultPhoto

from _reqOpenAI import *

#? Inline Query Handler
from uuid import uuid4
async def inline_query_initial(update: Update, context: ContextTypes.DEFAULT_TYPE):         #? inline_query_initial -- with end of the query model ("\\")
    #*****************Wrapper Function for inline_query()*******************
    global INL_QUERY_TIME
    query = update.inline_query.query
    if query != "":
        query_len_limit = 230                               # This is the no. of characters that user can write in inline query
        if (len(query) <= query_len_limit):
            query = query.strip()
            if query.endswith('\\\\'):
                # update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Generating!🔄, Please wait.....",input_message_content=InputTextMessageContent("Not Valid!"))])
                await inline_query(update, context, query.rstrip("\\\\"))
            else:
                await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Put \'\\\\\' at the end to Generarte Text Completion",input_message_content=InputTextMessageContent("Not Valid!"))])
        else:
            await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description=f"Warning!! Query must not exceed {query_len_limit} characters",input_message_content=InputTextMessageContent("Not Valid!"))])
    else:
        await update.inline_query.answer(results=[InlineQueryResultArticle(id=str(uuid4()),title="ChatAI",description="Hello!, Start writing to Generate. (end your query with \'\\\\\')",input_message_content=InputTextMessageContent("Not Valid!"))])

#* This code is Efficient to provide Real Time "Text Completion", 
#* though becuase to avoid unnessary (tons) of OpenAI API requests, 
#* and also as it produces high amount of machine load (which if not be handled correctly by the machine, it can produce unexpected results), 
#* hence to avoid this we made a wrapper function inline_query_initial(), 
#* which will allow this function to run only if the user put '\\' at the end of its query.
async def inline_query (update: Update, context: ContextTypes.DEFAULT_TYPE, query) -> None:
    #* Send OpenAI Request
    chat_id = str(update.inline_query.from_user.id)
    response, prob_file, generated = await send_req_openai_chat(update, query, chat_id, True)
    
    if generated:
        results = [
            InlineQueryResultArticle(                                       #* https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py
                id = str(uuid4()),
                title = "ChatAI",
                description = query[:50],
                input_message_content = InputTextMessageContent(response)
                # thumb_url = 'https://ibb.co/ZJ3tzKb'
                # reply_markup = InlineKeyboardMarkup(inline_keyboard)          # You can generate an inline keyboard too
            )
        ]
        #* Display Pop-up
        await update.inline_query.answer(results=results)
    else:
        update.inline_query.answer(results="ERROR OCCURED!")
    