import json
f = open("./out.json", "r")
file = f.read()
f.close
figures = json.loads(file)
tgbot = figures['result']
try:
    print(tgbot[0]['message']['reply_to_message']['message_id'])
except:
    print("hello")
