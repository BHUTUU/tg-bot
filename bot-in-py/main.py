import json, re, asyncio, aiohttp, time
from pathlib import Path
#<<<-----------Load config----------->>>
def parsejson(infile, tofind):
    with open(infile, "r") as f:
        figures = json.load(f)
    return figures[tofind]
#<<<-----------Internal variables----------->>>
tgbot = parsejson("/etc/secrets/config.json", "tgbot")
BOT_TOKEN = tgbot[0]['botToken']
BOT_NAME = tgbot[0]['botName']
OWNER_ID = tgbot[0]['ownerId']
ADMIN1 = tgbot[0]['admin1']
tgurl = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEND_MESSAGE = '/sendMessage'
GET_UPDATES = '/getUpdates'
EDIT_MESSAGE = '/editMessageText'
DELETE_MESSAGE = '/deleteMessage'
#<<<-----------Verify update ID----------->>>
def check_updates(upId):
    if not Path("updateid.txt").exists():
        open("updateid.txt", "a").close()
    with open("updateid.txt", "r") as f:
        return "no" if upId in f.read() else "yes"
#<<<-----------Admin check----------->>>
def admin_verify(adminId):
    return str(adminId) in (str(OWNER_ID), str(ADMIN1))
#<<<-----------Send message----------->>>
async def send_message(session, chat_id, text, message_id=None):
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'html',
        'disable_web_page_preview': True,
    }
    if message_id:
        data['reply_to_message_id'] = message_id
    async with session.post(tgurl + SEND_MESSAGE, data=data) as resp:
        return await resp.text()
#<<<-----------Edit message----------->>>
async def edit_message(session, chat_id, msgid, text):
    data = {
        'chat_id': chat_id,
        'message_id': msgid,
        'text': text,
        'parse_mode': 'html',
    }
    async with session.post(tgurl + EDIT_MESSAGE, data=data) as resp:
        return await resp.text()
#<<<-----------Delete message----------->>>
async def delete_message(session, chat_id, msgid):
    data = {
        'chat_id': chat_id,
        'message_id': msgid,
    }
    async with session.post(tgurl + DELETE_MESSAGE, data=data) as resp:
        return await resp.text()
#<<<-----------Dictionary meaning----------->>>
async def dictionary(session, word):
    async with session.get(f"http://api.urbandictionary.com/v0/define?term={word}") as resp:
        data = await resp.json()
    meaning = "\n".join([item['definition'] for item in data.get("list", [])])
    return meaning or "No definition found."
#<<<-----------Ping-pong latency check----------->>>
async def ping_latency(session):
    url = tgurl + GET_UPDATES
    start = time.perf_counter()
    try:
        async with session.post(url, data={'offset': '-1'}) as resp:
            await resp.json()
    except Exception as e:
        return f"Ping failed: {e}"
    end = time.perf_counter()
    latency_ms = round((end - start) * 1000, 2)
    return f"<code>pong!</code> ⏱️ {latency_ms} ms"
#<<<-----------Help Message----------->>>
Help_message="""
=========================
command             usage
--------------------------------------------------
/help       |- for this help menu.
/github    |- to get my github.
/id        |- to get my website.
/ping     |- measure the ping latency.
/mean     |- to get meaning of the provided word.
/sed newMessage   |- edit my message to which its replied.
/dt    |- delete a particular message
/pd    |- to delete all messages from replied message.
search Replace any string in message:
s/wordToReplace/newWord
________________________________"""
#<<<-----------Main polling loop----------->>>
async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.post(tgurl + GET_UPDATES, data={'offset': '-1'}) as resp:
                    updates = await resp.json()
            except:
                print("Internet connection issue")
                await asyncio.sleep(1)
                continue
            try:
                result = updates["result"][0]
                upid = str(result["update_id"])
            except:
                await asyncio.sleep(0.5)
                continue
            if check_updates(upid) == "no":
                continue
            else:
                with open("updateid.txt", "a") as f:
                    f.write(upid + "\n")
            try:
                msg = result['message']['text']
                chat = result['message']['chat']['id']
                fromid = result['message']['from']['id']
                username = result['message']['from'].get('username', 'User')
                message_id = result['message']['message_id']
                reply_to_id = result['message'].get('reply_to_message', {}).get('message_id')
                reply_to_text = result['message'].get('reply_to_message', {}).get('text', "")
            except:
                continue
            cmd = msg.split()[0]
            args = msg[len(cmd):].strip() if len(msg) > len(cmd) else ""
            if str(cmd).endswith(f"@{BOT_NAME}"):
                cmd = cmd.split("@")[0]
            #<<<-----------Command handling----------->>>
            match cmd:
                case "/mean":
                    if not args:
                        await send_message(session, chat, "Provide a word!", message_id)
                    else:
                        meaning = await dictionary(session, args)
                        await send_message(session, chat, meaning, message_id)
                case "/ping":
                    latency = await ping_latency(session)
                    await send_message(session, chat, latency, message_id)
                case "/help":
                    await send_message(session, chat, Help_message, message_id)
                case "/id":
                    await send_message(session, chat, f"<code>chat: {chat}</code>\n<code>you: {fromid}</code>", message_id)
                case "/github":
                    await send_message(session, chat, "https://github.com/BHUTUU", message_id)
                case "/start":
                    await send_message(session, chat, f"Hi! @{username} . Status: Running..!", message_id)
                case "/sed":
                    if not admin_verify(fromid):
                        await send_message(session, chat, "You are not authorized to use this command.", message_id)
                    elif not args:
                        await send_message(session, chat, "Provide the sentence to replace!", message_id)
                    elif reply_to_id:
                        await edit_message(session, chat, reply_to_id, args)
                    else:
                        await send_message(session, chat, "Reply to the message you want to edit.", message_id)
                case "/dt":
                    if not admin_verify(fromid):
                        await send_message(session, chat, "You are not authorized to use this command.", message_id)
                    elif reply_to_id:
                        await delete_message(session, chat, reply_to_id)
                        await delete_message(session, chat, message_id)
                    else:
                        await send_message(session, chat, "Reply to the message you want to delete!", message_id)
                case "/pd":
                    if not admin_verify(fromid):
                        await send_message(session, chat, "You are not authorized to use this command.", message_id)
                    elif reply_to_id:
                        try:
                            delete_tasks = [
                                delete_message(session, chat, msgid)
                                for msgid in range(reply_to_id, message_id + 1)
                            ]
                            await asyncio.gather(*delete_tasks)
                        except:
                            await send_message(session, chat, "Error deleting messages.", message_id)
                    else:
                        await send_message(session, chat, "Reply to the message from where to delete!", message_id)
            #<<<-----------Keyword responses----------->>>
            if msg.upper() in ["HELLO", "GOOD MORNING", "PLEASE HELP", "HELP ME"]:
                response_map = {
                    "HELLO": f"Hello @{username}",
                    "GOOD MORNING": f"Good morning @{username}",
                    "PLEASE HELP": f"Just explain your help/need and have patience @{username}",
                    "HELP ME": f"Just explain your help/need and have patience @{username}",
                }
                await send_message(session, chat, response_map[msg.upper()], message_id)
            #<<<-----------Search and Replace logic----------->>>
            if msg.startswith("s/"):
                try:
                    _, old, new = msg.split("/", 2)
                    if reply_to_text:
                        new_msg = reply_to_text.replace(old, new)
                        await send_message(session, chat, new_msg, reply_to_id)
                except:
                    pass
            await asyncio.sleep(0.2)
#<<<-----------Run the bot----------->>>
if __name__ == "__main__":
    asyncio.run(main())
