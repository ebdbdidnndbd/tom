import os, sys, asyncio, importlib
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# إعدادات السحب
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION_STR = sys.argv[1] if len(sys.argv) > 1 else ""

# 🛠️ الحل الجذري لمشكلة 'NoneType' في استضافة ديسكورد
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
# تهيئة الكاش يدوياً غصب قبل أي عملية
client.session.entities = {} 

PLUGINS_HELP = {}

def load_all():
    """ترتيب الملحقات المسحوبة تلقائياً"""
    if not os.path.exists("plugins"): return
    sys.path.insert(0, os.getcwd())
    for file in os.listdir("plugins"):
        if file.endswith(".py") and not file.startswith("__"):
            name = f"plugins.{file[:-3]}"
            try:
                mod = importlib.import_module(name)
                PLUGINS_HELP[getattr(mod, "SECTION_NAME", file)] = getattr(mod, "COMMANDS", "")
            except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help(event):
    # التأكد من إصلاح الجلسة داخل الحدث أيضاً
    if event.client.session.entities is None:
        event.client.session.entities = {}
    
    msg = "🚀 **أوامر سورس كـومن المرتبة:**\n━━━━━━━━━━━━━━━━━━\n"
    for sec, cmds in PLUGINS_HELP.items():
        msg += f"\n🔹 **{sec}:**\n{cmds}\n"
    await event.edit(msg)

async def run_engine():
    # إصلاح نهائي قبل الاتصال
    client.session.entities = {} 
    await client.connect()
    load_all() 
    await client.send_message("me", "✅ **تم تشغيل المحرك وإصلاح أخطاء الاستضافة بنجاح!**")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run_engine())
