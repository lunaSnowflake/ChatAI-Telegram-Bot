import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
RATE, RATING, ASK_DONATION, DONATE, FEEDBACK = range(5)
# Callback data
ONE, TWO, THREE, FOUR, FIVE = range(5)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hi! rate us /rate")
    
def rate(update: Update, context: CallbackContext) -> int:
    """Send message on `/rate`."""
    # Get user that sent /rate and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    
    keyboard = [
        [
            InlineKeyboardButton("Yep! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Later 😟", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Would You Like to Rate us? 😊", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `RATE` now
    return RATE

def yesRate(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
            InlineKeyboardButton("3", callback_data=str(THREE)),
            InlineKeyboardButton("4", callback_data=str(FOUR)),
            InlineKeyboardButton("5", callback_data=str(FIVE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="How would you like to Rate us?", reply_markup=reply_markup
    )
    return RATING

def noRate(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Rate next time! 😀 /rate"
    )
    return ConversationHandler.END

def one(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("I Do! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Nah! doing good!", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="It's Hard to see that! 😔\nDo you have any suggestion to Improve?", reply_markup=reply_markup
    )
    return FEEDBACK

def two(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("I Do! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Nah! doing good!", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Thanks for the Rating Us 2 Stars!\nDo you have any suggestion to Improve?", reply_markup=reply_markup
    )
    return FEEDBACK

def three(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("I Do! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Nah! doing good!", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Thanks for the Rating Us 3 Stars!😃\nDo you have any suggestion to Improve?", reply_markup=reply_markup
    )
    return FEEDBACK

def yesFeed(update: Update, context: CallbackContext) -> int:
    """Give Feedback"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Write us on <a href='https://dull-ground-8c3.notion.site/ChatAI-fd50caa64d9145b8a492e1a0eee3d831'>ChatAI</a>", parse_mode='HTML')
    return ConversationHandler.END

def noFeed(update: Update, context: CallbackContext) -> int:
    """No Feedback"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="You can rate us again anytime! 😀 /rate")
    return ConversationHandler.END

def four(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Ofcourse! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Nah! I'm broke 😶", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Thanks for the Rating Us 4 Stars!😀\nWould you like to Donate Us? 😋", reply_markup=reply_markup
    )
    return ASK_DONATION

def five(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Ofcourse! 😀", callback_data=str(ONE)),
            InlineKeyboardButton("Nah! I'm broke 😶", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Thanks for the Rating Us 5 Stars!😀\nWould you like to Donate Us? 😋", reply_markup=reply_markup
    )
    return ASK_DONATION

def yesDonate(update: Update, context: CallbackContext) -> int:
    """Donate"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$10", callback_data=str(ONE)),
            InlineKeyboardButton("$30", callback_data=str(TWO)),
            InlineKeyboardButton("$50", callback_data=str(THREE)),
            InlineKeyboardButton("$100", callback_data=str(FOUR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Any Donation Will Be Appreciated! 😊", reply_markup=reply_markup
    )
    return DONATE

def noDonate(update: Update, context: CallbackContext) -> int:
    """No Donate"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Us Bro Us 😔")
    return ConversationHandler.END

def Dollar10(update: Update, context: CallbackContext) -> int:
    """$$$ Donation"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Thanks for Donating $10! 😀\n Let me Buy a Coffee! ☕")
    return ConversationHandler.END

def Dollar30(update: Update, context: CallbackContext) -> int:
    """$$$ Donation"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Thanks for Donating $30! 😀\n Let me Buy an Ice Cream! 🍦")
    return ConversationHandler.END

def Dollar50(update: Update, context: CallbackContext) -> int:
    """$$$ Donation"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Thanks for Donating $50! 😀\n Let me Buy a Cake! 🎂")
    return ConversationHandler.END

def Dollar100(update: Update, context: CallbackContext) -> int:
    """$$$ Donation"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Thanks for Donating $100! 😀\n Let me Buy a Pizza! 🍕")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5900509062:AAERrExaFolQTo-ZAFe4uU5IarvONRmVqNk", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('rate', rate)],
        states={
            RATE: [
                CallbackQueryHandler(yesRate, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(noRate, pattern='^' + str(TWO) + '$'),
            ],
            RATING: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(five, pattern='^' + str(FIVE) + '$')
            ],
            ASK_DONATION: [
                CallbackQueryHandler(yesDonate, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(noDonate, pattern='^' + str(TWO) + '$')
            ],
            DONATE: [
                CallbackQueryHandler(Dollar10, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(Dollar30, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(Dollar50, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(Dollar100, pattern='^' + str(FOUR) + '$')
            ],
            FEEDBACK: [
                CallbackQueryHandler(yesFeed, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(noFeed, pattern='^' + str(TWO) + '$')
            ]
        },
        fallbacks=[CommandHandler('rate', rate)]
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()