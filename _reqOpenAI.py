from telegram import Update
from decouple import config
import openai
import aiohttp

from _userSettings import *

#********************************************* Send the Requests to OPENAI *************************************************
api_key = config('OPENAI_API_KEY')
    
#? Check if user don't send OpenAI requests more than max limit
def check_req_validity(chat_id):
    req_limit = 50
    status = False
    filename = '_userSettings.json'
    
    # Read file contents
    with open(filename, "r") as file:
        data = json.load(file)

    # Update json object
    from datetime import datetime
    lt_req = data[chat_id]['last_openai_req']
    lt_req = datetime.strptime(lt_req, '%Y-%m-%d %H:%M:%S').date()
    today = datetime.now().date()
    if (today > lt_req):                                                #? Check last request time if it was not made today
        data[chat_id]['num_openai_req'] = 0
            
    data[chat_id]['last_openai_req'] = datetime.now().isoformat(sep=" ", timespec="seconds")
    if (data[chat_id]['num_openai_req'] >= req_limit):                  #? Check number of requests
        status = False
    else:   
        data[chat_id]['num_openai_req'] += 1
        status = True
    
    # Write json file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
        
    return status

#? Adjust max token length
def adj_tokenLen(user_text, max_length, model):
    import re, math
    # compute no. of user tokens
    nTokens = len(re.split(r'[` \-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?]', user_text))
    nTokens += math.ceil((nTokens*0.3)) # adding buffer
    # compute model's max_tokens
    max_tokens = 4096 if (model == "text-davinci-003") else 2048
    # Total_Tokens (user tokens + max_length) must not be greater than model's max_tokens
    Total_Tokens = max_length + nTokens
    max_length = (max_tokens-nTokens) if (Total_Tokens > max_tokens) else max_length
    return max_length
    
#? Save User Queries to Database
def query_DB(user_text):
    import json
    with open("_QueryDB.json",'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside Queries
        file_data["Queries"].append(user_text)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

#? Make Text Completion Request
async def request_completions(user_text, chat_id, is_defualt=False):
    
    #* Retrive User's OpenAI Settings
    model, temperature, max_length, stop, top_p, frequency_penalty, presence_penalty, best_of, n, gen_probs = comd_val(chat_id, 'model', 'temperature', 'max_length', 'stop', 'top_p', 'frequency_penalty', 'presence_penalty', 'best_of', 'n', 'gen_probs')

    #* Adjust max token length
    max_length = adj_tokenLen(user_text, max_length, model)
        
    # Set the API endpoint
    api_endpoint = "https://api.openai.com/v1/completions"
    
    # Set the HTTP headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    gen_probs = 0 if gen_probs else None
    
    # Set the request body
    if (not is_defualt):
        data = f"""
        {{
            "model": {json.dumps(model)},
            "prompt": {json.dumps(user_text)},
            "temperature": {json.dumps(temperature)},
            "max_tokens": {json.dumps(max_length)},
            "stop": {json.dumps(stop)},
            "top_p": {json.dumps(top_p)},
            "frequency_penalty": {json.dumps(frequency_penalty)},
            "presence_penalty": {json.dumps(presence_penalty)},
            "best_of" : {json.dumps(best_of)},
            "n": {json.dumps(n)},
            "logprobs": {json.dumps(gen_probs)},
            "user": {json.dumps('user' + chat_id)}
        }}"""
    else:
        data = """
        {
            "model": "%s",
            "prompt": "%s",
        }
        """ % (model, user_text)
        
    # Create an async session
    async with aiohttp.ClientSession() as session:
        # Make the request to the API using the session's post() method
        async with session.post(api_endpoint, headers=headers, data=data) as response:
            # Check the status code of the response
            if response.status == 200:
                completions = await response.json()
                return completions
            else:
                err = await response.text()
                err = json.loads(err)
                raise Exception(err['error']['message'])
            
#? Generate Text Completion
async def send_req_openai_chat (update: Update, user_text, chat_id, isInlineReq):
    #* save user queries
    query_DB('chat:' + user_text)
    
    #* Check if user can send OpenAI request
    status = check_req_validity(chat_id)
    
    prob_file_name = None
    if status:
        #* Query Response
        response = await request_completions(user_text, chat_id, is_defualt=False)
        text_resp = response["choices"][0]["text"]
        #* Generate Probability File
        gen_probs = comd_val(chat_id, 'gen_probs')[0]
        if gen_probs and (not isInlineReq):
            token_logprobs = response["choices"][0]["logprobs"]["token_logprobs"]
            tokens = response["choices"][0]["logprobs"]["tokens"]
            try:
                #* scrape out tokens after "<|endoftext|>"
                end_text = tokens.index('<|endoftext|>')
                tokens = tokens[:end_text]
                token_logprobs = token_logprobs[:end_text]
            except Exception:
                pass
            finally:
                #* Calculate Probability
                from math import exp
                token_probs = list(map(exp, token_logprobs))
                #* Make Probability HTML File
                prob_file_name = response['id'] + ".html"
                with open (prob_file_name,"w") as f:
                    html_str = f"<html><head></head><body><h1>{user_text}</h1><h2>"
                    for i, elem in enumerate(tokens):
                        # Color Coding
                        if (0 <= token_probs[i] < 0.1):
                            color = "#FF6E6E"
                        elif (0.1 <= token_probs[i] < 0.2):
                            color = "#FF8282"
                        elif (0.2 <= token_probs[i] < 0.3):
                            color = "#FF9696"
                        elif (0.3 <= token_probs[i] < 0.4):
                            color = "#FFC8C8"
                        elif (0.4 <= token_probs[i] < 0.5):
                            color = "#FFE6E6"
                        elif (0.5 <= token_probs[i] < 0.6):
                            color = "#DAFF9F"
                        elif (0.6 <= token_probs[i] < 0.7):
                            color = "#8CFF8C"
                        elif (0.7 <= token_probs[i] < 0.8):
                            color = "#78F878"
                        elif (0.8 <= token_probs[i] < 0.9):
                            color = "#64E464"
                        else:
                            color = "#5ADA5A"
                        html_str = html_str + f"<span style=\"background-color: {color}\">{elem}</span>"
                            
                    html_str = html_str + "</h2></body></html>"
                    f.write(html_str)
    else:
        text_resp = "⚠ Oop! Maximum Request Limit Reached for Today. 😔\nTry Again Tommorrow! 😀"
        return text_resp, prob_file_name
    return text_resp, prob_file_name

#? Make Image Request
async def request_image(user_text, chat_id):
    # Set the API endpoint and headers
    endpoint = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Set the request body
    data = f"""
    {{
        "prompt": "{user_text}",
        "num_images":1,
        "size":"1024x1024",
        "user": {json.dumps('user' + chat_id)}
    }}
    """

    # Send the request
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=data) as response:
            # Check the status code
            if response.status == 200:
                return await response.json()
            else:
                err = await response.text()
                err = json.loads(err)
                raise Exception(err['error']['message'])
        
#? Image Generation
async def send_req_openai_image (update: Update, user_text, chat_id, isInlineReq):
    #* save user queries
    query_DB('image:' + user_text)
    
    #* Check if user can send OpenAI request
    status = check_req_validity(chat_id)

    if status:
        #* Query Response
        response =  await request_image(user_text, chat_id)
        response = response['data'][0]['url']
        return response, False
    else:
        response = "⚠ Oop! Maximum Request Limit Reached for Today. 😔\nTry Again Tommorrow! 😀"
        return response, True
    
#********************************************* Test OPENAI *************************************************
def send_req_openai_chat2(update, user_text, chat_id, isInlineReq):
    text_resp = "OpenAI response :: " + str(user_text).upper()
    return text_resp, None, True
    