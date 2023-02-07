from datetime import datetime, timezone
import aiohttp
from decouple import config
import json


# ***********************************************************User Info****************************************************************
#? Get User Info
async def new_user_api (update, chat_id, try_again=False):
    api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/userinfo/{chat_id}"

    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=None)
    now_time = str(utc_time.isoformat(sep=" ", timespec="seconds"))
    
    if not try_again:
        #* Payload -- handle for null values
        UserInfo = json.dumps({
            "chat_id": chat_id,
            "type": "private",
            "username": "" if update.message.from_user.username is None else update.message.from_user.username,
            "first_name": "" if update.message.from_user.first_name is None else update.message.from_user.first_name,
            "last_name": "" if update.message.from_user.last_name is None else update.message.chat.last_name,
            "time": now_time
        })
    else:
        #* Payload -- Add User With no other info  --  # Just a provision for "Invalid request body" -- if values cannot be parse to json   
        UserInfo = json.dumps({
            "chat_id": chat_id,
            "type": "private",
            "username": "",
            "first_name": "",
            "last_name": "",
            "time": now_time
        })
        
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's post() method
        async with session.post(api_endpoint, headers=headers, data=UserInfo) as response:
            # Check the status code of the response
            if response.status == 400 and not try_again:
                return await new_user_api (update, chat_id, try_again=True)

            return response.status

# ***********************************************************User Settings****************************************************************
#? Get User Setting(s)
async def get_user_setting_api (chat_id, sett=None):
    if sett is None:
        # Get All Settings
        api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"
    else:
        # Get only Specific Setting
        api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}&setting={sett}"
    
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Authorization': authkey
    }
    
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's get() method
        async with session.get(api_endpoint, headers=headers) as response:
            return await response.text()

#? Add new user settings(default)
async def new_setting_api (chat_id):
    api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"
   
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's post() method
        async with session.post(api_endpoint, headers=headers) as response:
            return response.status

#? update user settings
async def update_setting_api (chat_id, settings = {}):
    api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"

    payload = json.dumps(settings)      # if settings are empty -> fall back to default settings
    
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's put() method
        async with session.put(api_endpoint, headers=headers, data=payload) as response:
            return response.status

#? Add user query
async def queryDB_api (chat_id, user_text, type):
    api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/userquery"

    payload ={
        "chat_id": chat_id,
        "query": user_text,
        "type": type,
        "time": str(datetime.now().isoformat(sep=" ", timespec="seconds"))
    }
        
    payload = json.dumps(payload)

    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's post() method
        async with session.post(api_endpoint, headers=headers, data=payload) as response:
            return response.status

# settings = {
#         "model": "text-davinci-003"
#     }
# # print(update_setting_api("844328819", settings))

# print(json.loads(get_user_setting ("844328819")).get('settings'))

# val = int(json.loads(get_user_setting ("844328819", sett='num_openai_req')).get('settings'))
# print(type(val))
# print(val)

# from datetime import datetime
# today = datetime.now().date()
# lt_req = json.loads(get_user_setting ("844328819", "last_openai_req")).get('settings')
# lt_req = datetime.strptime(lt_req, '%Y-%m-%d %H:%M:%S').date()
# print(lt_req, type(lt_req))
# print(today, type(today))
# print(today > lt_req)