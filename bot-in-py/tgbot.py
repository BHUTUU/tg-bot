import json, requests, re, time
from pathlib import Path
from threading import Thread
#<<<-----PARSE JSON CONFIG FILE----->>>#
def parsejson(infile, tofind):
    f = open(infile, "r")
    file = f.read()
    f.close
    figures = json.loads(file)
    parsedData = figures[tofind]
    return parsedData
#<<<-----INTERNAL VARIABLES----->>>#
tgbot=parsejson("./config.json", "tgbot")
tgurl="https://api.telegram.org/bot"
BOT_TOKEN=tgbot[0]['botToken']
#CHAT_ID=tgbot[0]['chatId']
SEND_MESSAGE='/sendMessage'
GET_UPDATES='/getUpdates'
EDIT_MESSAGE ='/editMessageText'
DELETE_MESSAGE='/deleteMessage'
TEXT_MESSAGE="?&text="
#msg_to_send=""
#<<<-----UPDATE VERIFICATION----->>>#
def checkUpdates(upId):
    validity=""
    updateFile = open("updateid.txt", "r")
    for word in updateFile:
        if (re.search(upId,word)):
            validity="no"
            break
        else:
            validity="yes"
    return validity
#<<<-----ADMIN VERIFICATION----->>>#
def adminVerify(adminId):
    admin=tgbot[0]['ownerId']
    admin2=tgbot[0]['admin1']
    if(str(admin) == str(adminId)):
        return True
    elif(str(admin2) == str(adminId)):
        return True
    else:
        return False
#<<<-----SEND MESSAGE----->>>#
#def sendMessage(msg_to__send, chat__id):#, message_id):
def sendMessage(msg_to__send, message_id, chat__id):
    data = {
        'chat_id': int(chat__id),
        'parse_mode': 'html',
        'disable_web_page_preview': 'true',
        'reply_to_message_id': int(message_id),
        'text': str(msg_to__send),
    }
    #response = requests.post(tgurl+BOT_TOKEN+SEND_MESSAGE+chat_id+TEXT_MESSAGE+msg_to_send.replace(" ", '%20'))
    response = requests.post(tgurl+BOT_TOKEN+SEND_MESSAGE, data=data)
#    print(response.text)
#<<<-----Edit Message----->>>#
def editMessage(chatid, msgid, messagetext):
    data = {
        'chat_id': int(chatid),
        'parse_mode': 'html',
        'disable_web_page_preview': 'true',
        'message_id': int(msgid),
        'text': str(messagetext),
    }
    respEdit = requests.post(tgurl+BOT_TOKEN+EDIT_MESSAGE, data=data)
#    print(respEdit.text)
    return respEdit.text
#<<<-----DELETE MESSAGE------>>>#
def deleteMessage(chat__id, message__id):
    data = {
        'chat_id': int(chat__id),
        'message_id': int(message__id),
    }
    respDel = requests.post(tgurl+BOT_TOKEN+DELETE_MESSAGE, data=data)
#    print(respDel.text)
    return respDel.text
#<<<-----UPDATES MANAGER----->>>#
def getUpdates():
    data = {
        'offset': '-1',
    }
    resp = requests.post(tgurl+BOT_TOKEN+GET_UPDATES, data=data)
    outjson=open("out.json", "w")
    outjson.write(resp.text)
    outjson.close()
#<<<===========FUNCTIONS FOR MANAGEMENT OF GROUP OR PERSONAL CHATS===========>>>#
#<<<----DICTIONARY----->>>#
def dictionary(wordToMean):
    meaning=""
    meaningjson = requests.get(f"http://api.urbandictionary.com/v0/define?term={wordToMean}")
    outjson=open("out.json", "w")
    outjson.write(meaningjson.text)
    outjson.close()
    result=parsejson("out.json", "list")
    i=0
    while(i<=(len(result) - 1)):
        meaning+="\n"+result[i]['definition']
        i+=1
    return meaning
def helpMenu():
    toHelp="""
=========================
command             usage
--------------------------------------------------
/help       |- for this help menu.
/github    |- to get my github.
/id        |- to get my website.
/mean     |- to get meaning of the provided word.
/sed newMessage   |- edit my message to which its replied.
/dt    |- delete a particular message
/pd    |- to delete all messages from replied message.
search Replace any string in message:
s/wordToReplace/newWord
________________________________"""
    return toHelp

#<<<-------NON ADMIN R3STRICTION------>>>#
def authfailMessage(warn_message, chat, message_id2):
    for i in warn_message.split():
        editMessage(str(chat), message_id2, i)
        time.sleep(0.01)
#<<<--------MAIN MANAGER-------->>>#
while True:
    upfile=Path("updateid.txt")
    if not upfile.is_file():
        open("updateid.txt", "a").close()
    try:
        getUpdates()
    except:
        print("Internet connection breaks")
    result=parsejson("out.json","result")
    try:
        upid=result[0]["update_id"]
    except:
        continue
    valid = checkUpdates(str(upid))
    if (valid == "no"):
        continue
    else:
        with open("updateid.txt", "a") as fileToUp:
            fileToUp.write(str(upid)+"\n")
            fileToUp.close()
    msg=result[0]['message']['text']
    chat=result[0]['message']['chat']['id']
    fromid=result[0]['message']['from']['id']
    fromusr=result[0]['message']['from']['username']
    message_id=result[0]['message']['message_id']
    try:
        message_id2=result[0]['message']['reply_to_message']['message_id']
        message_got=result[0]['message']['reply_to_message']['text']
    except:
        pass
    cmd=str(msg).split()[0]
    if(str(cmd).find("@") != -1):
        pingcmd=cmd.replace("@", " ")
        cmd=pingcmd.split()[0]
    args=re.sub(r'.', '', str(msg), count=(len(cmd) + 1))
    #sentRespose=sendMessage(str(msg), str(chat))
    #print(sentRespose)
    match cmd:
        case "/mean":
            if not args:
                sendMessage("provide a word!", message_id, str(chat))
            else:
                wordmean=dictionary(str(args))
                sendMessage(str(wordmean), message_id, str(chat))
        case "/help":
            helpmsg=helpMenu()
            sendMessage(str(helpmsg), message_id, str(chat))
        case "/github":
            sendMessage("https://github.com/BHUTUU", message_id, str(chat))
        case "/website":
            sendMessage("bhutuu.github.io", message_id, str(chat))
        case "/ping":
            sendMessage("<code>pong!</code>", message_id, str(chat))
        case "/start":
            sendMessage("Hi! @"+str(fromusr)+" . Status: Running..!", message_id, str(chat))
        case "/sed":
            if adminVerify(fromid):
                   if not args:
                       sendMessage("provide the sentance to replace!", message_id, str(chat))
                   else:
                       editMessage(str(chat), message_id2, str(args))
            else:
                if not args:
                    sendMessage("you are not authotised to use this cmd", message_id, str(chat))
                else:
                    authfailMessage("hey! you are not allowed to edit any message from me!", str(chat), message_id2)
                    editMessage(str(chat), message_id2, str(message_got))
        case "/dt":
            if adminVerify(fromid):
                try:
                    deleteMessage(chat, message_id2)
                    deleteMessage(chat, message_id)
                except:
                    sendMessage("reply to any message which you want to delete!", message_id, str(chat))
            else:
                sendMessage("you are not authotised to use this cmd", message_id, str(chat))
        case "/pd":
            if adminVerify(fromid):
                try:
                    test = message_id2
                    try:
                        threads = [Thread(target=deleteMessage, args=(chat,i))
                                for i in list(range(int(test),int(message_id)+1,1))]
                        for thread in threads:
                            thread.start()
                        for thread in threads:
                            thread.joint()
                    except:
                        pass
                except:
                    sendMessage("reply to any message from where u want to delete the chats!", message_id, str(chat))
            else:
                sendMessage("you are not authotised to use this cmd", message_id, str(chat))

#<<<-------MESSAGE REACTION------->>>#
    match msg.upper():
        case "GOOD MORNING":
            sendMessage("Good morning @"+str(fromusr), message_id, str(chat))
        case "HELLO":
            sendMessage("Hello @"+str(fromusr), message_id, str(chat))
        case "PLEASE HELP":
            sendMessage("Just explain your help/need and have patience @"+str(fromusr), message_id, str(chat))
        case "HELP ME":
            sendMessage("Just explain your help/need and have patience @"+str(fromusr), message_id, str(chat))
#<<<-----SEARCH AND REPLACE------>>>#
    if (msg.find('s/', 0, 2) != -1):
        text1 = msg.split('/')[1]
        text2 = msg.split('/')[2]
        try:
            newMess = message_got.replace(text1, text2)
            sendMessage(str(newMess), message_id2, str(chat))
        except:
            pass
