import os, asyncio, json, logging, time, subprocess, sys
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, UserNotParticipantError, FloodWaitError
from datetime import datetime
from typing import Dict
import threading

# =========================================================
# ⚙️ الإعدادات الثابتة
# =========================================================
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'
BOT_TOKEN = '8307560710:AAFNRpzh141cq7rKt_OmPR0A823dxEaOZVU'
REQUIRED_CHANNEL = 'iomk3' 
SUPPORT_USER = "iomk0"
VIDEO_FILE = '1000008567.mp4' if os.path.exists('1000008567.mp4') else None

# إعدادات التسجيل
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =========================================================
# 📊 نظام إدارة المستخدمين (مبسط بدون ربح)
# =========================================================
class CloudUserManager:
    def __init__(self):
        self.active_users: Dict[int, Dict] = {}
        self.load_users()
        
    def load_users(self):
        """تحميل المستخدمين"""
        try:
            if os.path.exists('cloud_users.json'):
                with open('cloud_users.json', 'r', encoding='utf-8') as f:
                    self.active_users = json.load(f)
                logger.info(f"تم تحميل {len(self.active_users)} مستخدم")
        except Exception as e:
            logger.error(f"خطأ في التحميل: {e}")
            
    def save_users(self):
        """حفظ المستخدمين"""
        try:
            with open('cloud_users.json', 'w', encoding='utf-8') as f:
                json.dump(self.active_users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطأ في الحفظ: {e}")
            
    def add_user(self, user_id: int, phone: str, name: str):
        """إضافة مستخدم جديد"""
        self.active_users[str(user_id)] = {
            'phone': phone,
            'name': name,
            'join_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': True,
            'status': 'connected'
        }
        self.save_users()
        logger.info(f"تم إضافة المستخدم: {name}")

# =========================================================
# 🤖 فئة اليوزربوت (بدون مخازن - بدون ربح)
# =========================================================
class CloudUserBot:
    def __init__(self, session_str: str, user_id: int, phone: str, name: str):
        self.client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        self.user_id = user_id
        self.phone = phone
        self.name = name
        self.session_str = session_str
        self.is_running = False
        self.manager = cloud_manager
        self.restart_attempts = 0
        self.max_restarts = 100  # عدد محاولات إعادة التشغيل
        
    async def setup_user(self):
        """إعداد المستخدم فقط"""
        try:
            # التحقق من القناة الإجبارية
            if REQUIRED_CHANNEL:
                try:
                    await self.client(GetParticipantRequest(channel=REQUIRED_CHANNEL, participant=self.user_id))
                except Exception as e:
                    logger.warning(f"User {self.user_id} not in channel: {e}")
                    try:
                        await self.client(JoinChannelRequest(REQUIRED_CHANNEL))
                    except:
                        pass
            
            # ✅ تشغيل السورس الرئيسي في خيط منفصل مع إعادة تشغيل تلقائي
            def run_main_with_restart():
                attempts = 0
                while attempts < self.max_restarts:
                    try:
                        logger.info(f"تشغيل main.py للمستخدم {self.user_id} - المحاولة {attempts + 1}")
                        
                        # تشغيل السورس مع إعدادات منع التوقف
                        process = subprocess.Popen(
                            ["python3", "main.py", self.session_str],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE
                        )
                        
                        # مراقبة العملية
                        while True:
                            # التحقق من أن العملية لا تزال تعمل
                            if process.poll() is not None:
                                logger.warning(f"السورس توقف للمستخدم {self.user_id}، إعادة التشغيل...")
                                break
                            
                            # إرسال أمر حيوي للحفاظ على الاتصال
                            try:
                                if attempts % 10 == 0:  # كل 10 دورات
                                    process.stdin.write(b"\n")
                                    process.stdin.flush()
                            except:
                                pass
                            
                            time.sleep(30)  # انتظار 30 ثانية قبل الفحص التالي
                        
                        attempts += 1
                        time.sleep(5)  # انتظار 5 ثواني قبل إعادة التشغيل
                        
                    except Exception as e:
                        logger.error(f"خطأ في تشغيل main.py للمستخدم {self.user_id}: {e}")
                        time.sleep(10)
                        attempts += 1
            
            # تشغيل السورس في خيط منفصل
            thread = threading.Thread(target=run_main_with_restart, daemon=True)
            thread.start()
            
            # إرسال الكليشة والفيديو الترحيبي
            welcome_private = f"""🔥 **تم تفعيل حسابك في سورس كومن السحابي بنجاح!**

╔══════════════════════════════════════╗
║          🚀 سورس كومن السحابي       ║
╚══════════════════════════════════════╝

👤 **المستخدم:** {self.name}
📱 **الهاتف:** {self.phone}
🆔 **الايدي:** `{self.user_id}`
📅 **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚡ **الحالة:** ✅ متصل بالخادم الرئيسي

✨ **مميزات النظام:**
• ⚡ سرعة فائقة في الأداء
• 🔒 تشفير متقدم وأمان كامل
• 🛡 حماية من التوقف التلقائي
• 🔄 تحديثات مستمرة
• 📊 استقرار عالي

🚀 **كيفية الاستخدام:**
1. انتظر اكتمال تحميل السورس (10 ثواني)
2. اكتب `.الاوامر` لعرض جميع الأوامر
3. اكتب `.فحص` لاختبار سرعة السورس
4. اكتب `.معلومات` لعرض معلومات الحساب

📞 **الدعم الفني:** @{SUPPORT_USER}
📢 **قناة السورس:** @{REQUIRED_CHANNEL}

🔧 **معلومات الخادم:**
• الخادم: سيرفر مركزي متقدم
• النظام: يعمل 24/7 بدون توقف
• النسخة: السحابية المستقرة
• المطور: @{SUPPORT_USER}

⚡ **تم تفعيل جميع ميزات السورس بنجاح!**"""
            
            # إرسال الرسالة أولاً
            await self.client.send_message("me", welcome_private)
            
            # إرسال الفيديو مع نفس الكليشة
            if VIDEO_FILE and os.path.exists(VIDEO_FILE):
                try:
                    await self.client.send_file(
                        "me", 
                        VIDEO_FILE, 
                        caption=welcome_private
                    )
                except Exception as e:
                    logger.error(f"خطأ في إرسال الفيديو: {e}")
            
            # إضافة المستخدم
            self.manager.add_user(self.user_id, self.phone, self.name)
            
            logger.info(f"✅ تم تفعيل الحساب: {self.name} ({self.user_id})")
            return True
            
        except FloodWaitError as e:
            logger.error(f"FloodWait للمستخدم {self.user_id}: {e.seconds} ثانية")
            return False
        except Exception as e:
            logger.error(f"Setup error: {e}")
            return False
    
    async def keep_alive(self):
        """الحفاظ على اتصال اليوزربوت حياً"""
        while self.is_running:
            try:
                # التحقق من أن اليوزربوت لا يزال متصلاً
                if not self.client.is_connected():
                    logger.warning(f"اليوزربوت {self.user_id} فقد الاتصال، إعادة الاتصال...")
                    await self.client.connect()
                
                # إرسال أمر حيوي كل 5 دقائق
                await self.client.send_message("me", "🔄 السورس يعمل...")
                await asyncio.sleep(300)  # 5 دقائق
                
            except Exception as e:
                logger.error(f"خطأ في keep_alive للمستخدم {self.user_id}: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة قبل إعادة المحاولة
    
    async def start(self):
        """بدء التشغيل - بدون توقف"""
        self.is_running = True
        
        while self.is_running and self.restart_attempts < self.max_restarts:
            try:
                logger.info(f"بدء تشغيل اليوزربوت {self.user_id} - المحاولة {self.restart_attempts + 1}")
                
                # الاتصال
                await self.client.connect()
                
                if not await self.client.is_user_authorized():
                    logger.error(f"المستخدم {self.user_id} غير مصرح له")
                    self.is_running = False
                    return
                
                # الإعداد
                if await self.setup_user():
                    logger.info(f"✅ اليوزربوت {self.user_id} يعمل بنجاح")
                    
                    # بدء مهمة الحفاظ على الحياة
                    keep_alive_task = asyncio.create_task(self.keep_alive())
                    
                    # البقاء متصلاً للأبد
                    await self.client.run_until_disconnected()
                    
                    # إذا وصلنا هنا، تم قطع الاتصال
                    logger.warning(f"✅ تم قطع اتصال اليوزربوت {self.user_id}، إعادة التشغيل...")
                    
                    # إلغاء مهمة keep_alive
                    keep_alive_task.cancel()
                    
                else:
                    logger.error(f"❌ فشل إعداد اليوزربوت {self.user_id}")
                
                self.restart_attempts += 1
                
                # انتظار قبل إعادة المحاولة
                if self.is_running and self.restart_attempts < self.max_restarts:
                    logger.info(f"⏳ انتظار 10 ثواني قبل إعادة تشغيل اليوزربوت {self.user_id}...")
                    await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ خطأ في اليوزربوت {self.user_id}: {e}")
                self.restart_attempts += 1
                
                if self.is_running and self.restart_attempts < self.max_restarts:
                    logger.info(f"⏳ انتظار 15 ثواني قبل إعادة المحاولة للمستخدم {self.user_id}...")
                    await asyncio.sleep(15)
        
        self.is_running = False
        logger.info(f"⏹ توقف اليوزربوت {self.user_id} بعد {self.restart_attempts} محاولات")

# =========================================================
# 🌐 النظام السحابي
# =========================================================
cloud_manager = CloudUserManager()
active_userbots: Dict[int, CloudUserBot] = {}
login_states = {}

async def start_user_session(user_id: int, session_str: str, phone: str, name: str):
    """بدء جلسة مستخدم - بدون توقف"""
    if user_id in active_userbots:
        try:
            active_userbots[user_id].is_running = False
            await active_userbots[user_id].client.disconnect()
            del active_userbots[user_id]
        except:
            pass
    
    # إنشاء يوزربوت جديد
    userbot = CloudUserBot(session_str, user_id, phone, name)
    active_userbots[user_id] = userbot
    
    # التشغيل في الخلفية بدون انتظار
    asyncio.create_task(userbot.start())
    
    return userbot

# =========================================================
# 🤖 بوت التنصيب
# =========================================================
bot = TelegramClient('CloudInstallerBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """واجهة البدء"""
    try:
        # التحقق من وجود رابط إحالة
        if len(event.text.split()) > 1:
            ref_code = event.text.split()[1]
            # يمكنك حفظ كود الإحالة هنا إذا أردت
            pass
        
        user = await event.get_sender()
        
        welcome_msg = f"""⚡ **مرحباً {user.first_name or ''} في سورس كومن السحابي** ⚡

🚀 **النظام السحابي المتكامل**
✨ **تنصيب سريع واستقرار دائم**

🎯 **مميزات السورس:**
• ✅ تشغيل فوري بدون انتظار
• ⚡ سرعة عالية واستجابة سريعة
• 🔒 أمان تام وحماية متقدمة
• 🛡 يعمل 24/7 بدون توقف
• 🔄 تحديثات تلقائية

📊 **ماذا ستحصل عليه:**
• جميع أوامر السورس الرئيسي
• اتصال مباشر بالخادم المركزي
• دعم فني متواصل
• استقرار عالي الأداء

👇 **اضغط للبدء في التنصيب:**"""
        
        buttons = [
            [Button.inline("🚀 تنصيب السورس الآن", b'start_installation')],
            [Button.url("📢 قناة السورس", "https://t.me/iomk3"), Button.url("👨‍💻 المطور", f"https://t.me/{SUPPORT_USER}")]
        ]
        
        await event.respond(welcome_msg, buttons=buttons)
        
    except Exception as e:
        logger.error(f"خطأ في start_handler: {e}")
        await event.respond("🚀 **أهلاً بك! اضغط للبدء:**", buttons=[[Button.inline("🚀 بدء التنصيب", b'start_installation')]])

@bot.on(events.CallbackQuery(data=b'start_installation'))
async def start_installation_handler(event):
    """بدء عملية التنصيب"""
    try:
        chat_id = event.chat_id
        
        # إلغاء أي عملية سابقة
        if chat_id in login_states:
            try:
                await login_states[chat_id]['client'].disconnect()
            except:
                pass
            del login_states[chat_id]
        
        # إنشاء عميل جديد
        new_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await new_client.connect()
        
        login_states[chat_id] = {
            'client': new_client,
            'step': 'phone',
            'start_time': time.time(),
            'attempts': 0
        }
        
        await event.edit(
            """🚀 **مرحلة التنصيب - الخطوة 1**

📞 **أرسل رقم هاتفك مع رمز الدولة:**
مثال: `+9647701234567`

⚡ **جاري التحضير للنظام السحابي...**
⏱ **المدة المتوقعة:** 20 ثانية فقط""",
            buttons=[[Button.inline("❌ إلغاء", b'cancel')]]
        )
        
    except Exception as e:
        logger.error(f"خطأ في start_installation_handler: {e}")
        await event.answer("❌ حدث خطأ، حاول مرة أخرى")

@bot.on(events.NewMessage)
async def handle_messages(event):
    """معالجة الرسائل"""
    try:
        chat_id = event.chat_id
        text = event.text.strip()
        
        if not text or text == '/start':
            return
        
        # التحقق من حالة تسجيل الدخول
        if chat_id not in login_states:
            return
        
        state = login_states[chat_id]
        await handle_login_process(event, state)
        
    except Exception as e:
        logger.error(f"خطأ في handle_messages: {e}")

async def handle_login_process(event, state):
    """معالجة عملية تسجيل الدخول"""
    chat_id = event.chat_id
    text = event.text.strip()
    client = state['client']
    
    try:
        if state['step'] == 'phone':
            send_code = await client.send_code_request(text)
            
            state.update({
                'phone': text,
                'phone_code_hash': send_code.phone_code_hash,
                'step': 'code',
                'attempts': 0
            })
            
            await event.respond(
                """✅ **تم إرسال كود التحقق**

📲 **الخطوة 2:** أرسل الكود الذي وصلك
مثال: `12345` أو `1 2 3 4 5`

⚡ **جاري إعداد الخادم السحابي...**""",
                buttons=[[Button.inline("🔄 إعادة إرسال", b'resend_code'), Button.inline("❌ إلغاء", b'cancel')]]
            )
            
        elif state['step'] == 'code':
            code = text.replace(' ', '')
            
            try:
                await client.sign_in(
                    phone=state['phone'],
                    code=code,
                    phone_code_hash=state['phone_code_hash']
                )
            except SessionPasswordNeededError:
                state['step'] = 'password'
                await event.respond(
                    "🔐 **الخطوة 3:** الحساب محمي بكلمة سر\n"
                    "🔑 **أرسل كلمة السر الآن:**"
                )
                return
            
            await process_successful_login(event, client, state)
            
        elif state['step'] == 'password':
            await client.sign_in(password=text)
            await process_successful_login(event, client, state)
            
    except PhoneCodeInvalidError:
        state['attempts'] += 1
        if state['attempts'] >= 3:
            await event.respond("❌ **تم تجاوز عدد المحاولات**")
            if chat_id in login_states:
                try:
                    await login_states[chat_id]['client'].disconnect()
                except:
                    pass
                del login_states[chat_id]
        else:
            await event.respond(f"❌ **الكود غير صحيح**\nالمحاولات المتبقية: {3 - state['attempts']}")
    except Exception as e:
        logger.error(f"خطأ في handle_login_process: {e}")
        await event.respond(f"⚠️ **حدث خطأ:** {str(e)}")
        if chat_id in login_states:
            try:
                await login_states[chat_id]['client'].disconnect()
            except:
                pass
            del login_states[chat_id]

async def process_successful_login(event, client, state):
    """معالجة تسجيل الدخول الناجح"""
    try:
        # الحصول على معلومات الحساب
        me = await client.get_me()
        session_str = client.session.save()
        
        # إرسال رسالة التحميل
        loading_msg = await event.respond("""
⚡ **جاري تنصيب السورس السحابي...**

🔄 **مراحل التنصيب:**
1. ✅ تحميل بيانات الحساب
2. 🔄 الاتصال بالخادم الرئيسي
3. 🚀 تشغيل السورس الأساسي
4. 📊 إعداد النظام الكامل

⏱ **جاري العمل، الرجاء الانتظار...**""")
        
        # بدء الجلسة السحابية
        userbot = await start_user_session(
            me.id,
            session_str,
            state['phone'],
            me.first_name or me.username or "مستخدم"
        )
        
        if userbot:
            # رسالة النجاح النهائية
            success_msg = f"""🎉 **تم التنصيب بنجاح!**

✅ **الحساب:** {me.first_name or me.username}
📱 **الرقم:** {state['phone']}
🆔 **الايدي:** `{me.id}`
⚡ **الحالة:** متصل بالخادم السحابي

🚀 **تم تفعيل جميع ميزات السورس:**
• ✅ السورس الرئيسي يعمل
• ✅ جميع الأوامر مفعلة
• ✅ اتصال مستمر 24/7
• ✅ تحديثات تلقائية

💡 **للبدء الآن:**
1. اذهب للرسائل المحفوظة (Saved Messages)
2. اكتب `.الاوامر` لعرض القائمة
3. اكتب `.فحص` لاختبار النظام
4. اكتب `.معلومات` لعرض بياناتك

📢 **القناة:** @{REQUIRED_CHANNEL}
👨‍💻 **الدعم:** @{SUPPORT_USER}

🔥 **السورس يعمل الآن بدون توقف!**"""
            
            # إرسال الفيديو مع الرسالة
            try:
                if VIDEO_FILE and os.path.exists(VIDEO_FILE):
                    await bot.send_file(
                        event.chat_id,
                        VIDEO_FILE,
                        caption=success_msg
                    )
                else:
                    await bot.send_message(event.chat_id, success_msg)
            except Exception as e:
                logger.error(f"خطأ في إرسال الفيديو: {e}")
                await bot.send_message(event.chat_id, success_msg)
            
            # إرسال تأكيد إضافي
            await bot.send_message(
                event.chat_id,
                "✅ **تم اكتمال التنصيب بنجاح!**\n\n"
                "⚡ **السورس يعمل الآن في حسابك.**\n"
                "📱 **انتقل للرسائل المحفوظة للبدء.**\n\n"
                "🛡 **معلومة:** النظام يعمل تلقائياً ولا يتوقف."
            )
            
        else:
            await event.respond("⚠️ **حدث خطأ في التنصيب**\n\nيرجى المحاولة مرة أخرى.")
            
    except Exception as e:
        logger.error(f"خطأ في process_successful_login: {e}")
        await event.respond(f"⚠️ **حدث خطأ:** {str(e)}")
    finally:
        # تنظيف
        if event.chat_id in login_states:
            try:
                await login_states[event.chat_id]['client'].disconnect()
            except:
                pass
            del login_states[event.chat_id]

@bot.on(events.CallbackQuery(data=b'resend_code'))
async def resend_code_handler(event):
    """إعادة إرسال الكود"""
    try:
        if event.chat_id in login_states:
            state = login_states[event.chat_id]
            send_code = await state['client'].send_code_request(state['phone'])
            state['phone_code_hash'] = send_code.phone_code_hash
            await event.answer("✅ تم إعادة إرسال الكود")
    except Exception as e:
        logger.error(f"خطأ في resend_code_handler: {e}")
        await event.answer("❌ فشل إعادة الإرسال")

@bot.on(events.CallbackQuery(data=b'cancel'))
async def cancel_handler(event):
    """إلغاء العملية"""
    try:
        if event.chat_id in login_states:
            try:
                await login_states[event.chat_id]['client'].disconnect()
            except:
                pass
            del login_states[event.chat_id]
        
        await event.edit("❌ **تم إلغاء العملية**", buttons=[[Button.inline("🚀 البدء من جديد", b'start_installation')]])
    except Exception as e:
        logger.error(f"خطأ في cancel_handler: {e}")

# =========================================================
# 🚀 تشغيل النظام الرئيسي
# =========================================================
async def main():
    """الدالة الرئيسية"""
    print("""
╔══════════════════════════════════════════╗
║     🚀 سورس كومن السحابي - الإصدار     ║
║           المستقر بدون توقف            ║
╠══════════════════════════════════════════╣
║ ✅ النظام: سحابي يعمل 24/7             ║
║ ⚡ المميزات:                             ║
║   • بدون مخازن رسائل                    ║
║   • بدون نظام ربح                       ║
║   • إرسال كليشة ترحيبية                 ║
║   • إرسال فيديو ترحيبي                  ║
║   • تشغيل السورس بدون توقف              ║
╠══════════════════════════════════════════╣
║ 👨‍💻 المطور: @iomk0                      ║
║ 📢 القناة: @iomk3                       ║
║ ⏱ وقت البدء: {}                ║
╚══════════════════════════════════════════╝

🚀 جاري تشغيل النظام السحابي...
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    # تشغيل البوت
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        # إعدادات لمنع التوقف
        import signal
        signal.signal(signal.SIGINT, lambda s, f: None)
        
        # تشغيل النظام
        bot.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n✅ تم إيقاف النظام يدوياً")
    except Exception as e:
        logger.critical(f"خطأ في النظام الرئيسي: {e}")
        print(f"\n❌ خطأ: {e}")
    finally:
        print("👋 تم إغلاق النظام السحابي")
