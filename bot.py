import os, asyncio, subprocess, sys, shutil, logging
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# --- الإعدادات الرسمية (بياناتك) ---
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
REPO_URL = "https://github.com/ebdbdidnndbd/tom.git"

# تنظيف سجلات التيرمينال لضمان عدم الدوخة
logging.basicConfig(level=logging.ERROR)

class MasterEngine:
    """المحرك الذكي لسحب الأوامر وترتيبها غصب"""
    @staticmethod
    def setup_and_sync(user_id):
        user_dir = f"user_{user_id}"
        if os.path.exists(user_dir): shutil.rmtree(user_dir)
        
        # سحب الملفات عبر جيثب حصراً بنظام السحب السريع
        try:
            subprocess.run(["git", "clone", "--depth", "1", REPO_URL, user_dir], check=True, capture_output=True)
            # تنصيب المكاتب تلقائياً وبصمت (بدون sqlite3)
            libs = "telethon requests edge-tts aiohttp beautifulsoup4 deep-translator langdetect uvloop"
            subprocess.run(f"pip3 install {libs} -q", shell=True)
            return user_dir
        except: return None

# واجهة البوت المنصب
bot = TelegramClient('Installer', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
sessions = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("⚡ **منصب سورس كـومن الموحد**\nسأقوم بسحب أوامرك من جيثب وتشغيل المحرك فوراً.", 
                        buttons=[[Button.inline("🚀 بدء التنصيب", b'run')]])

@bot.on(events.CallbackQuery(data=b'run'))
async def login_start(event):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    sessions[event.chat_id] = {'c': client, 'step': 'phone'}
    await event.edit("📞 **أرسل رقم هاتفك الآن:**")

@bot.on(events.NewMessage)
async def login_handler(event):
    cid = event.chat_id
    if cid not in sessions or event.text == '/start': return
    st = sessions[cid]
    if st['step'] == 'phone':
        res = await st['c'].send_code_request(event.text)
        st.update({'phone': event.text, 'hash': res.phone_code_hash, 'step': 'code'})
        await event.respond("✅ **أرسل كود التحقق:**")
    elif st['step'] == 'code':
        await st['c'].sign_in(st['phone'], event.text.replace(' ', ''), phone_code_hash=st['hash'])
        me = await st['c'].get_me()
        session_str = st['c'].session.save()
        await event.respond("⏳ **المحرك يسحب الأوامر الآن...**")
        path = MasterEngine.setup_and_sync(me.id)
        if path:
            os.chdir(path)
            subprocess.Popen([sys.executable, "main.py", session_str]) # تشغيل اليوزربوت
            await event.respond(f"🎊 **تم تفعيل السورس يا {me.first_name}!**")
        del sessions[cid]

bot.run_until_disconnected()
