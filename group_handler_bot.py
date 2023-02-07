from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.ext import (
    Application,
    ChatMemberHandler,
    ContextTypes
)
from typing import Optional, Tuple

import json
from decouple import config

# Enable logging
import logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
        of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
        the status didn't change.
        --------------------------------------
        If a user joins the group, OLD status will be "LEFT" and NEW status will be "MEMBER", 
        while if user left the group, OLD status: "MEMBER\OWNER\ADMINISTRATOR" and NEW status: "LEFT" 
    """ 
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))
    
    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member

async def send_group_intro(update):
    await update.effective_chat.send_message(f'''
Hi I am <a href='https://t.me/chaii_test_bot'>ChatAI</a>, Thanks for adding me!😊
Let's make your group super productive. 🚀
I can help you with :
• Text Completion | 
    use: /text $your_query$
• Image Generation | 
    use: /img $your_query$
This Bot is based on <a href='https://bit.ly/OpenAI_Introduction'>OpenAI</a>
'''
            , disable_web_page_preview=True
            , parse_mode='HTML'
        )
    
async def group_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #* Send Bot Intro to New Group
    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        result = extract_status_change(update.my_chat_member)
        if result is None:
            return
        
        was_member, is_member = result
        if not was_member and is_member:
            await send_group_intro(update)
            
async def update_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #* We will only track users coming in and out for our(Admin) group and channel
    admin_group_id = config('ADMIN_GROUP_ID')
    admin_channel_id = config('ADMIN_CHANNEL_ID')
    # admin_group_id = -1001891225073
    # admin_channel_id = -1001857203404
    if update.chat_member.chat.id == admin_group_id or update.chat_member.chat.id == admin_channel_id:
        
        chat_id = str(update.chat_member.from_user.id)
        
        result = extract_status_change(update.chat_member)
        if result is None:
            return
        
        was_member, is_member = result
    
        if update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP]: filename = 'group_users.json'
        if update.effective_chat.type == Chat.CHANNEL: filename = 'channel_users.json'
        
        #* Add user to group_users/channel_users file
        if not was_member and is_member:  
            with open(filename,'r+') as file:
                file_data = json.load(file)
                file_data.append(chat_id)
                file.seek(0)
                json.dump(file_data, file, indent = 4)
    
        #* Remove user from group_users/channel_users file
        elif was_member and not is_member:
            with open(filename,'r') as file:
                file_data = json.load(file)

            file_data.remove(chat_id)
            with open(filename,'w') as file:
                json.dump(file_data, file, indent = 4)

def main() -> None:
    from decouple import config
    BOT_TOKEN = config('TELE_BOT_API_KEY_3')
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(ChatMemberHandler(update_chat_members, ChatMemberHandler.CHAT_MEMBER))
    # application.add
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()