# main.py
import os, sys, asyncio, importlib, logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# بياناتك الرسمية
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
# تأكد من وضع جلستك هنا أو استلامها من نظام التنصيب
SESSION = os.environ.get("SESSION", "") 

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
PLUGINS_HELP = {}

def load_all_plugins():
    """المحرك العالمي: يقرأ، يحمل، ويفعل الأوامر غصب"""
    global PLUGINS_HELP
    PLUGINS_HELP.clear()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_path = os.path.join(base_dir, "plugins")
    if not os.path.exists(plugin_path): os.makedirs(plugin_path)

    sys.path.insert(0, base_dir)

    for file in os.listdir(plugin_path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = f"plugins.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
                
                # --- الخطوة اللي جانت ناقصة: تسجيل الأوامر في الكلاينت ---
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # إذا جان الفانكشن عليه @events.register، نسجله هسة
                    if hasattr(attr, 'event'):
                        client.add_event_handler(attr)
                
                # سحب كليشة المساعدة
                s_name = getattr(module, "SECTION_NAME", None)
                s_cmds = getattr(module, "COMMANDS", None)
                if s_name and s_cmds:
                    PLUGINS_HELP[s_name] = s_cmds
                print(f"✅ تم تفعيل وتسجيل إضافات: {file}")
            except Exception as e:
                print(f"❌ فشل تسجيل {file}: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الاوامر'))
async def help_menu(event):
    """عرض قائمة الأوامر الموحدة"""
    if not PLUGINS_HELP: load_all_plugins()
    menu = "🚀 **قائمة أوامر سـورس كـومـن العالمي**\n━━━━━━━━━━━━━━━━━━\n"
    for sec, cmds in PLUGINS_HELP.items():
        menu += f"\n🔹 **{sec}:**\n{cmds}\n"
    menu += "\n━━━━━━━━━━━━━━━━━━\n👨‍💻 المطور: @iomk0"
    await event.edit(menu)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فحص'))
async def ping(event):
    """أمر فحص سريع للتأكد من أن المحرك يعمل"""
    await event.edit("⚡ **المحرك العالمي شغال 100%!**\n📡 جميع الأوامر مسجلة ونشطة.")

async def start_common():
    await client.connect()
    if not await client.is_user_authorized(): 
        print("❌ الجلسة غير صالحة!")
        return
    
    load_all_plugins()
    print("🚀 سورس كومن شغال والأوامر تفعلت تلقائياً!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_common())
