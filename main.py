import os, sys, asyncio, importlib, logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# إعدادات الدخول
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION = sys.argv[1] if len(sys.argv) > 1 else ""

# --- تنظيف تام (صاروخي) ---
logging.basicConfig(level=logging.CRITICAL)  # فقط الكوارث
for logger_name in ["telethon", "yt_dlp", "aiohttp", "asyncio", "urllib3"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# خيارات صاروخية للعميل
client = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH,
    connection_retries=None,  # لانهائي
    request_retries=10,
    auto_reconnect=True,
    flood_sleep_threshold=120
)

PLUGINS_HELP = {}
PLUGINS_CACHE = {}

def load_plugins():
    """محرك صاروخي لتحميل الملحقات"""
    global PLUGINS_HELP, PLUGINS_CACHE
    
    path = "plugins"
    if not os.path.exists(path): 
        os.makedirs(path)
    
    # تحميل متوازي سريع
    for file in os.listdir(path):
        if file.endswith(".py") and not file.startswith("__"):
            name = f"plugins.{file[:-3]}"
            try:
                # تحميل ذكي مع كاش
                if name not in PLUGINS_CACHE:
                    spec = importlib.util.spec_from_file_location(
                        name, os.path.join(path, file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    spec.loader.exec_module(module)
                    PLUGINS_CACHE[name] = module
                
                module = PLUGINS_CACHE[name]
                
                # استخراج المساعدة فوراً
                s_name = getattr(module, "SECTION_NAME", "🛠️ عام")
                s_cmds = getattr(module, "COMMANDS", "لا توجد أوامر")
                PLUGINS_HELP[s_name] = s_cmds
            except Exception:
                continue

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_cmd(event):
    """أوامر صاروخية السرعة"""
    if not PLUGINS_HELP:
        load_plugins()
    
    # بناء الرسالة بسرعة
    sections = []
    for section, commands in sorted(PLUGINS_HELP.items()):
        sections.append(f"🔹 **{section}:**\n{commands}")
    
    msg = f"""🚀 **قائمة أوامر صاروخية** ⚡
━━━━━━━━━━━━━━━━━━
{"\n".join(sections)}

━━━━━━━━━━━━━━━━━━
⚡ السرعة: قصوى | 👨‍💻 @iomk0"""
    
    await event.edit(msg)

async def start_engine():
    """بدء تشغيل صاروخي"""
    try:
        await client.connect()
        if not await client.is_user_authorized(): 
            return
        
        # تحميل سريع مسبق
        load_plugins()
        
        # رسالة بداية خفيفة
        print("⚡ المحرك الصاروخي يعمل الآن!")
        
        # تشغيل دون تعليق
        await client.run_until_disconnected()
        
    except KeyboardInterrupt:
        pass
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # تشغيل بصورة صاروخية
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(start_engine())
    except KeyboardInterrupt:
        sys.exit(0)
