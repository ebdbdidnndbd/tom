import os, sys, asyncio, importlib, logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# إعدادات الدخول
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION = sys.argv[1] if len(sys.argv) > 1 else ""

# --- تنظيف التيرمينال (Silent Mode) ---
# جعل السجلات تظهر الأخطاء فقط لكي لا تزدحم الشاشة بالبحث والتحميل
logging.basicConfig(level=logging.ERROR)
for logger_name in ["telethon", "yt_dlp", "aiohttp"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
PLUGINS_HELP = {}

def load_plugins():
    """المحرك الذكي لترتيب وتحميل الملحقات تلقائياً"""
    global PLUGINS_HELP
    path = "plugins"
    if not os.path.exists(path): os.makedirs(path)
    
    sys.path.insert(0, os.getcwd())
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            name = f"plugins.{file[:-3]}"
            try:
                module = importlib.import_module(name)
                # سحب تعريفات المساعدة تلقائياً لترتيب القائمة
                s_name = getattr(module, "SECTION_NAME", "قسم غير معروف")
                s_cmds = getattr(module, "COMMANDS", "لا توجد أوامر")
                PLUGINS_HELP[s_name] = s_cmds
            except Exception as e:
                pass

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_cmd(event):
    """عرض قائمة الأوامر المرتبة تلقائياً"""
    msg = "🚀 **قائمة أوامر سـورس كـومن المرتبة**\n━━━━━━━━━━━━━━━━━━\n"
    for section, commands in PLUGINS_HELP.items():
        msg += f"\n🔹 **{section}:**\n{commands}\n"
    msg += "\n━━━━━━━━━━━━━━━━━━\n👨‍💻 @iomk0"
    await event.edit(msg)

async def start_engine():
    await client.connect()
    if not await client.is_user_authorized(): return
    load_plugins() # تحميل الأوامر فوراً
    print("🚀 المحرك الذكي يعمل الآن.. التيرمينال نظيف!")
    await client.send_message("me", "✅ **تم تفعيل المحرك الذكي وترتيب الأوامر بنجاح!**")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_engine())
