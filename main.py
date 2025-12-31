import os, sys, asyncio, importlib
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# بيانات الدخول المسحوبة من المحرك
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION = sys.argv[1] if len(sys.argv) > 1 else ""

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
PLUGINS_HELP = {}

def load_plugins():
    """محرك ترتيب الأوامر تلقائياً من مجلد plugins"""
    path = "plugins"
    if not os.path.exists(path): return
    sys.path.insert(0, os.getcwd())
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            mod_name = f"plugins.{file[:-3]}"
            try:
                mod = importlib.import_module(mod_name)
                # سحب بيانات المساعدة غصب
                PLUGINS_HELP[getattr(mod, "SECTION_NAME", file)] = getattr(mod, "COMMANDS", "")
            except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help(event):
    msg = "🚀 **أوامر سورس كـومن المسحوبة من جيثب:**\n━━━━━━━━━━━━━━━━━━\n"
    for sec, cmds in PLUGINS_HELP.items():
        msg += f"\n🔹 **{sec}:**\n{cmds}\n"
    await event.edit(msg)

async def start():
    await client.connect()
    load_plugins() # تحميل الأوامر المرتبة
    await client.send_message("me", "✅ **المحرك سحب جميع الأوامر وشغلها بنجاح!**")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start())
