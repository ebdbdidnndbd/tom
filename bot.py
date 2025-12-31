import os, asyncio, subprocess, sys, shutil, logging
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# --- الإعدادات الرسمية ---
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
REPO_URL = "https://github.com/ebdbdidnndbd/tom.git"

logging.basicConfig(level=logging.ERROR)

class DiscordManager:
    """المحرك الساحب للأوامر والمصلح للأخطاء"""
    @staticmethod
    def setup_user(user_id):
        user_dir = f"user_{user_id}"
        if os.path.exists(user_dir): shutil.rmtree(user_dir)
        
        try:
            # سحب الأوامر غصب عبر Git
            subprocess.run(["git", "clone", "--depth", "1", REPO_URL, user_dir], check=True, capture_output=True)
            # تنصيب المكاتب بصمت وتجنب خطأ sqlite3
            libs = "telethon requests edge-tts aiohttp beautifulsoup4 deep-translator langdetect uvloop"
            subprocess.run(f"pip3 install {libs} -q", shell=True)
            return user_dir
        except: return None

# واجهة البوت
bot = TelegramClient('Manager', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
logins = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🛡️ **منصب سورس كـومن (نسخة استضافة ديسكورد)**\nالمحرك جاهز لسحب الأوامر وإصلاح أخطاء الجلسة تلقائياً.", 
                        buttons=[[Button.inline("🚀 بدء التنصيب", b'go')]])

@bot.on(events.CallbackQuery(data=b'go'))
async def go(event):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    logins[event.chat_id] = {'c': client, 'step': 'phone'}
    await event.edit("📞 **أرسل رقم الهاتف مع مفتاح الدولة:**")

@bot.on(events.NewMessage)
async def handler(event):
    cid = event.chat_id
    if cid not in logins or event.text == '/start': return
    st = logins[cid]
    
    try:
        if st['step'] == 'phone':
            res = await st['c'].send_code_request(event.text)
            st.update({'phone': event.text, 'hash': res.phone_code_hash, 'step': 'code'})
            await event.respond("✅ **أرسل كود التحقق الآن:**")
        elif st['step'] == 'code':
            await st['c'].sign_in(st['phone'], event.text.replace(' ', ''), phone_code_hash=st['hash'])
            me = await st['c'].get_me()
            session = st['c'].session.save()
            
            await event.respond("⏳ **المحرك يسحب الأوامر ويصلح الجلسة غصب...**")
            path = DiscordManager.setup_user(me.id)
            if path:
                os.chdir(path)
                # تشغيل المحرك الرئيسي مع تمرير الجلسة
                subprocess.Popen([sys.executable, "main.py", session])
                await event.respond(f"🎊 **تم تفعيل السورس بنجاح يا {me.first_name}!**")
            del logins[cid]
    except Exception as e:
        await event.respond(f"❌ **حدث خطأ:** {str(e)}")
