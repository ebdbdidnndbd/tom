import os, asyncio, json, logging, time, subprocess, sys, threading, shutil, requests, importlib
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, UserNotParticipantError
from datetime import datetime
from typing import Dict

# =========================================================
# ⚙️ الإعدادات الأساسية
# =========================================================
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
REQUIRED_CHANNEL = 'iomk3' 
SUPPORT_USER = "iomk0"
GITHUB_REPO = "https://github.com/ebdbdidnndbd/tom.git"
VIDEO_FILE = '1000008567.mp4' if os.path.exists('1000008567.mp4') else None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =========================================================
# 🔧 نظام تفعيل المحرك السحابي الذكي
# =========================================================
class SourceActivator:
    @staticmethod
    def clone_and_setup(user_id: int, session_str: str):
        """استنساخ السورس وإعداد المحرك الذكي"""
        try:
            user_dir = f"user_{user_id}"
            if os.path.exists(user_dir): shutil.rmtree(user_dir)
            os.makedirs(user_dir, exist_ok=True)
            
            # 1. استنساخ السورس من GitHub
            clone_cmd = ["git", "clone", "--depth", "1", GITHUB_REPO, user_dir]
            subprocess.run(clone_cmd, capture_output=True, timeout=30)
            
            # 2. إنشاء ملف المحرك الرئيسي (الذي سيقوم بسحب الأوامر)
            SourceActivator.create_smart_main(user_dir)
            
            # 3. تثبيت المكتبات اللازمة
            SourceActivator.install_requirements(user_dir)
            
            return user_dir
        except Exception as e:
            logger.error(f"Error in setup: {e}")
            return None

    @staticmethod
    def create_smart_main(user_dir: str):
        """إنشاء محرك ذكي يبحث عن الملحقات ويظهر القائمة المساعدة غصب"""
        main_file = os.path.join(user_dir, "main.py")
        
        # محتوى ملف المحرك الذي سيعمل في حساب المستخدم
        main_content = '''import os, sys, asyncio, importlib, time
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# إعدادات المستخدم الثابتة
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
SESSION = sys.argv[1] if len(sys.argv) > 1 else ""

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
PLUGINS_HELP = {}

def load_plugins():
    """المحرك الذكي لسحب الملحقات والقائمة"""
    global PLUGINS_HELP
    PLUGINS_HELP.clear()
    
    # تحديد مسار الملحقات بدقة
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_path = os.path.join(base_dir, "plugins")
    
    if not os.path.exists(plugin_path): return
    
    sys.path.insert(0, base_dir)

    for file in os.listdir(plugin_path):
        if file.endswith(".py") and not file.startswith("__"):
            module_name = f"plugins.{file[:-3]}"
            try:
                # تحميل الموديول وسحب التعريفات منه
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)
                
                s_name = getattr(module, "SECTION_NAME", None)
                s_cmds = getattr(module, "COMMANDS", None)
                if s_name and s_cmds:
                    PLUGINS_HELP[s_name] = s_cmds
            except Exception as e:
                print(f"Error loading {file}: {e}")

@client.on(events.NewMessage(outgoing=True, pattern=r'\\.الاوامر'))
async def help_cmd(event):
    """عرض قائمة الأوامر المجمعة من كل الملحقات"""
    if not PLUGINS_HELP: load_plugins() # إعادة محاولة السحب
    
    if not PLUGINS_HELP:
        return await event.edit("⚠️ **لم يتم العثور على أوامر مسجلة في المحرك!**")

    msg = "🚀 **قائمة أوامر سـورس تـوم السـحابي**\\n━━━━━━━━━━━━━━━━━━\\n"
    for section, commands in PLUGINS_HELP.items():
        msg += f"\\n🔹 **{section}:**\\n{commands}\\n"
    msg += "\\n━━━━━━━━━━━━━━━━━━\\n👨‍💻 **المطور:** @iomk0"
    await event.edit(msg)

@client.on(events.NewMessage(outgoing=True, pattern=r'\\.فحص'))
async def ping(event):
    await event.edit("⚡ **سورس توم يعمل بنجاح!**\\n📡 تم تفعيل جميع الأوامر سحابياً.")

async def start_engine():
    await client.connect()
    if not await client.is_user_authorized(): return
    load_plugins() # تحميل الإضافات فور التشغيل
    await client.send_message("me", "✅ **تم تفعيل السورس وجلب جميع الأوامر بنجاح!**\\nاكتب `.الاوامر` للتجربة.")
    print("🚀 Engine started successfully")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(start_engine())
'''
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)

    @staticmethod
    def install_requirements(user_dir: str):
        """تثبيت المكتبات لضمان عمل كافة أوامر السورس"""
        req_file = os.path.join(user_dir, "requirements.txt")
        if os.path.exists(req_file):
            subprocess.run(["pip3", "install", "-r", req_file, "-q"])
        else:
            subprocess.run(["pip3", "install", "telethon", "requests", "edge-tts", "aiohttp", "-q"])

# =========================================================
# 🌪 محرك المستخدم السحابي (تشغيل وإدارة)
# =========================================================
class TurboUserBot:
    def __init__(self, session_str, user_id, phone, name):
        self.client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        self.user_id, self.phone, self.name, self.session = user_id, phone, name, session_str

    async def run(self):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized(): return
            
            # بدء الإعداد السريع
            user_dir = SourceActivator.clone_and_setup(self.user_id, self.session)
            if user_dir:
                # تشغيل المحرك كعملية منفصلة
                os.chdir(user_dir)
                subprocess.Popen(["python3", "main.py", self.session])
                return True
            return False
        except Exception as e:
            logger.error(f"Run error: {e}")
            return False

# =========================================================
# 🚀 بوت التنصيب (الواجهة الرئيسية)
# =========================================================
bot = TelegramClient('TurboInstallerBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
login_data = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    welcome = f"⚡ **أهلاً بك في منصب سورس توم السحابي**\n\nهذا البوت يقوم بتنصيب السورس وتفعيل جميع الأوامر في حسابك خلال ثوانٍ وبدون تيرمكس."
    await event.respond(welcome, buttons=[[Button.inline("🚀 ابدأ التنصيب الآن", b'install')]])

@bot.on(events.CallbackQuery(data=b'install'))
async def install_callback(event):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    login_data[event.chat_id] = {'client': client, 'step': 'phone'}
    await event.edit("📞 **أرسل رقم هاتفك الآن (مثال: +964...):**", buttons=[[Button.inline("❌ إلغاء", b'cancel')]])

@bot.on(events.NewMessage)
async def login_handler(event):
    chat_id = event.chat_id
    if chat_id not in login_data or event.text == '/start': return
    
    state = login_data[chat_id]
    client = state['client']
    text = event.text.strip()

    try:
        if state['step'] == 'phone':
            res = await client.send_code_request(text)
            state.update({'phone': text, 'phone_code_hash': res.phone_code_hash, 'step': 'code'})
            await event.respond("✅ **أرسل كود التحقق الآن:**")
        elif state['step'] == 'code':
            await client.sign_in(state['phone'], text.replace(' ', ''), phone_code_hash=state['phone_code_hash'])
            await setup_success(event, client, state)
    except Exception as e:
        await event.respond(f"⚠️ **حدث خطأ:** {e}")

async def setup_success(event, u_client, state):
    me = await u_client.get_me()
    session = u_client.session.save()
    await event.respond("⚡ **جاري تفعيل السورس وجلب الأوامر سحابياً...**")
    
    # تشغيل اليوزربوت السحابي
    user_bot = TurboUserBot(session, me.id, state['phone'], me.first_name)
    success = await user_bot.run()
    
    if success:
        caption = f"🎊 **تم التنصيب بنجاح!**\n\n👤 **المستخدم:** {me.first_name}\n🚀 **الحالة:** السورس شغال 24/7\n\n💡 اذهب للرسائل المحفوظة واكتب `.الاوامر`"
        if VIDEO_FILE: await bot.send_file(event.chat_id, VIDEO_FILE, caption=caption)
        else: await bot.send_message(event.chat_id, caption)
    
    del login_data[event.chat_id]

bot.run_until_disconnected()
