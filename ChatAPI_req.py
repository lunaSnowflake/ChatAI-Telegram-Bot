from datetime import datetime
import requests
from decouple import config
import json


# ***********************************************************User Info****************************************************************
'''#**************ASYNC version************
async def chat_ai_userinfo2():
    import json
    from decouple import config
    import aiohttp
    
    api_endpoint = "https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/userinfo/7064970"

    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "chat_id": "87896986",
        "type": "jia",
        "username": "jia",
        "first_name": "jia",
        "last_name": "jia",
        "time": "jia"
    })
        
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's post() method
        async with session.post(api_endpoint, headers=headers, data=payload) as response:
            # Check the status code of the response
            print(await response.text())
            print(response.status)'''

#? Get User Info
def new_user_api (update, chat_id, try_again=False):
    api_endpoint = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/userinfo/{chat_id}"

    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    
    if not try_again:
        #* Payload -- handle for null values
        UserInfo = json.dumps({
            "chat_id": chat_id,
            "type": "" if update.message.chat.type is None else update.message.chat.type,
            "username": "" if update.message.chat.username is None else update.message.chat.username,
            "first_name": "" if update.message.chat.first_name is None else update.message.chat.first_name,
            "last_name": "" if update.message.chat.last_name is None else update.message.chat.last_name,
            "time": str(datetime.now())
        })
    else:
        #* Payload -- Add User With no other info  --  # Just a provision for "Invalid request body" -- if values cannot be parse to json   
        UserInfo = json.dumps({
            "chat_id": chat_id,
            "type": "",
            "username": "",
            "first_name": "",
            "last_name": "",
            "time": str(datetime.now())
        })

    response = requests.request("POST", api_endpoint, headers=headers, data=UserInfo)
    
    if response.status_code == 400 and not try_again:
        return new_user_api (update, chat_id, try_again=True)
    
    return response.status_code

# ***********************************************************User Settings****************************************************************
#? Get User Setting(s)
def get_user_setting_api (chat_id, sett=None):
    if sett is None:
        # Get All Settings
        url = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"
    else:
        # Get only Specific Setting
        url = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}&setting={sett}"
    
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Authorization': authkey
    }

    response = requests.request("GET", url, headers=headers)

    return response.text

#? Add new user settings(default)
def new_setting_api (chat_id):
    url = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"
   
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }
    
    response = requests.request("POST", url, headers=headers)

    return response.status_code

#? update user settings
def update_setting_api (chat_id, settings = {}):
    url = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/usersettings?chat_id={chat_id}"

    payload = json.dumps(settings)      # if settings are empty -> fall back to default settings
    
    authkey = config("CHATAI_API_AUTH")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authkey
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    return response.status_code

#? Add user query
def queryDB_api (chat_id, user_text, type):
    url = f"https://2ksakimfoa.execute-api.ap-northeast-1.amazonaws.com/ChatAIAPI/userquery"

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
    
    response = requests.request("POST", url, headers=headers, data=payload)

    return response.status_code

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