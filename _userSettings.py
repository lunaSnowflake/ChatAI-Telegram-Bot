import json
#? Retrive User's OpenAI Setting
def comd_val (chat_id, *comd):
    filename = '_userSettings.json'
    # Read file contents
    with open(filename, "r") as file:
        data = json.load(file)
    # Retrieve all values for specified setting
    values = []
    for elem in comd:
        values.append(data[chat_id][elem])
    return values
    
