import os, json, aiohttp, asyncio, re, time
from aiohttp import web
from pathlib import Path

# <<<----------- Load Config ----------->>>
dotenv_data = os.environ.get("dotenvdata")
if dotenv_data:
    tgbot = json.loads(dotenv_data)["tgbot"]
else:
    print("Missing dotenvdata environment variable!")
    exit(1)

BOT_TOKEN = tgbot[0]['botToken']
BOT_NAME = tgbot[0]['botName']
OWNER_ID = tgbot[0]['ownerId']
ADMIN1 = tgbot[0]['admin1']

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8080") + WEBHOOK_PATH

# <<<----------- Helper Functions ----------->>>

def admin_verify(adminId):
    return str(adminId) in (str(OWNER_ID), str(ADMIN1))

async def send_message(session, chat_id, text, reply_to_id=None):
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'html',
        'disable_web_page_preview': True,
    }
    if reply_to_id:
        data['reply_to_message_id'] = reply_to_id
    async with session.post(TG_API + "/sendMessage", data=data) as resp:
        return await resp.text()

async def edit_message(session, chat_id, msgid, text):
    data = {'chat_id': chat_id, 'message_id': msgid, 'text': text, 'parse_mode': 'html'}
    async with session.post(TG_API + "/editMessageText", data=data) as resp:
        return await resp.text()

async def delete_message(session, chat_id, msgid):
    data = {'chat_id': chat_id, 'message_id': msgid}
    async with session.post(TG_API + "/deleteMessage", data=data) as resp:
        return await resp.text()

async def dictionary(session, word):
    try:
        async with session.get(f"http://api.urbandictionary.com/v0/define?term={word}") as resp:
            data = await resp.json()
        meaning = "\n".join([item['definition'] for item in data.get("list", [])])
        return meaning or "No definition found."
    except Exception as e:
        return f"Error fetching definition: {e}"

async def ping_latency(session):
    start = time.perf_counter()
    try:
        async with session.get(TG_API + "/getMe") as resp:
            await resp.json()
    except Exception as e:
        return f"Ping failed: {e}"
    end = time.perf_counter()
    latency_ms = round((end - start) * 1000, 2)
    return f"<code>pong!</code> ⏱️ {latency_ms} ms"

Help_message = """
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
________________________________
"""

# <<<----------- Webhook & Handlers ----------->>>

routes = web.RouteTableDef()

@routes.post(WEBHOOK_PATH)
async def handle_update(request):
    data = await request.json()
    message = data.get('message') or {}
    if not message:
        return web.Response(status=200)

    msg = message.get('text', '')
    chat = message.get('chat', {}).get('id')
    fromid = message.get('from', {}).get('id')
    username = message.get('from', {}).get('username', 'User')
    message_id = message.get('message_id')
    reply_to = message.get('reply_to_message', {})
    reply_to_id = reply_to.get('message_id')
    reply_to_text = reply_to.get('text', "")

    if not msg:
        return web.Response(status=200)

    cmd = msg.split()[0]
    args = msg[len(cmd):].strip() if len(msg) > len(cmd) else ""

    if str(cmd).endswith(f"@{BOT_NAME}"):
        cmd = cmd.split("@")[0]

    async with aiohttp.ClientSession() as session:
        # Command handling
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

        # Keyword responses
        if msg.upper() in ["HELLO", "GOOD MORNING", "PLEASE HELP", "HELP ME"]:
            responses = {
                "HELLO": f"Hello @{username}",
                "GOOD MORNING": f"Good morning @{username}",
                "PLEASE HELP": f"Just explain your help/need and have patience @{username}",
                "HELP ME": f"Just explain your help/need and have patience @{username}",
            }
            await send_message(session, chat, responses[msg.upper()], message_id)

        # Search and replace
        if msg.startswith("s/"):
            try:
                _, old, new = msg.split("/", 2)
                if reply_to_text:
                    new_msg = reply_to_text.replace(old, new)
                    await send_message(session, chat, new_msg, reply_to_id)
            except:
                pass

    return web.Response(status=200)

@routes.get("/")
async def health_check(request):
    return web.Response(text="✅ Bot is running on Render Web Service!")

async def set_webhook():
    async with aiohttp.ClientSession() as session:
        await session.post(f"{TG_API}/setWebhook", data={"url": WEBHOOK_URL})
        print(f"Webhook set to: {WEBHOOK_URL}")

async def init_app():
    app = web.Application()
    app.add_routes(routes)
    await set_webhook()
    return app

if __name__ == "__main__":
    web.run_app(init_app(), port=int(os.environ.get("PORT", 8080)))
