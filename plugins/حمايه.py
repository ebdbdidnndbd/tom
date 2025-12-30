import os, asyncio, time, json
from telethon import events, functions, types
from datetime import datetime

# =========================================================
# 🔧 الإعدادات الأساسية
# =========================================================
SECTION_NAME = "🛡 أوامر الحماية والخصوصية"
SAVE_DIR = "saved_media"
CONFIG_FILE = "protection_config.json"

# إنشاء مجلد الحفظ
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# 📊 تعريف الأوامر للمساعدة
# =========================================================
COMMANDS = {
    "الرئيسية": [
        "`.حماية` - عرض قائمة أوامر الحماية",
        "`.حماية [اسم]` - تفاصيل أمر محدد"
    ],
    "الحظر التلقائي": [
        "`.تفعيل الحظر` - حظر من يكرر الرسائل (3 رسائل)",
        "`.تعطيل الحظر` - إيقاف الحظر التلقائي",
        "`.عدد الحظر [رقم]` - تغيير عدد الرسائل المسموحة (افتراضي: 3)",
        "`.حظر يدوي @معرف` - حظر مستخدم يدوياً",
        "`.الغاء الحظر @معرف` - إلغاء حظر مستخدم"
    ],
    "الرد التلقائي": [
        "`.تفعيل الرد` - تفعيل الرد التلقائي للخاص",
        "`.تعطيل الرد` - إيقاف الرد التلقائي",
        "`.وضع رد [نص]` - تغيير رسالة الرد التلقائي",
        "`.وقت الرد [ثواني]` - تحديد وقت تأخير الرد"
    ],
    "وضع الشبح": [
        "`.تفعيل الشبح` - وضع القراءة المخفي (عدم الظهور أونلاين)",
        "`.تعطيل الشبح` - إيقاف وضع الشبح",
        "`.شبح للكل` - تطبيق الشبح على جميع الدردشات",
        "`.شبح خاص` - الشبح للخاص فقط"
    ],
    "حفظ الميديا": [
        "`.تفعيل الحفظ` - حفظ الصور والفيديوهات ذاتية التدمير",
        "`.تعطيل الحفظ` - إيقاف الحفظ التلقائي",
        "`.المحفوظات` - عرض الملفات المحفوظة",
        "`.مسح المحفوظات` - حذف جميع الملفات المحفوظة"
    ],
    "الإحصائيات": [
        "`.احصائيات الحماية` - عرض إحصائيات النظام",
        "`.المحظورين` - عرض قائمة المحظورين",
        "`.نسخة احتياطية` - حفظ الإعدادات"
    ]
}

# =========================================================
# ⚙️ إعدادات الحماية الافتراضية
# =========================================================
DEFAULT_CONFIG = {
    "auto_block": {
        "enabled": False,
        "max_messages": 3,
        "time_window": 60,
        "blocked_users": []
    },
    "auto_reply": {
        "enabled": False,
        "message": "👋 **أهلاً بك، أنا مشغول حالياً.**\n📞 **سيتم الرد عليك قريباً.**\n⏰ **الوقت:** {time}\n📅 **التاريخ:** {date}",
        "delay": 1,
        "exceptions": []
    },
    "ghost_mode": {
        "enabled": False,
        "for_all": False,
        "for_private": True,
        "last_seen": None
    },
    "auto_save": {
        "enabled": False,
        "save_path": SAVE_DIR,
        "saved_count": 0,
        "notify": True
    },
    "stats": {
        "total_blocked": 0,
        "total_replied": 0,
        "total_saved": 0,
        "last_activity": None
    }
}

# =========================================================
# 📁 نظام التحميل والحفظ
# =========================================================
class ProtectionManager:
    def __init__(self):
        self.config = self.load_config()
        self.flood_cache = {}
        self.user_cache = {}
        
    def load_config(self):
        """تحميل الإعدادات من الملف"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """حفظ الإعدادات إلى الملف"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def update_stats(self, key):
        """تحديث الإحصائيات"""
        if key in self.config["stats"]:
            self.config["stats"][key] += 1
        self.config["stats"]["last_activity"] = datetime.now().isoformat()
        self.save_config()

manager = ProtectionManager()

# =========================================================
# 🛠 معالج الأوامر الرئيسي
# =========================================================
@events.register(events.NewMessage(outgoing=True, pattern=r"^\.(حماية|حظر|الغاء|تفعيل|تعطيل|وضع|عدد|وقت|شبح|المحفوظات|مسح|احصائيات|المحظورين|نسخة)(?:\s+(.*))?$"))
async def protection_engine(event):
    try:
        cmd = event.pattern_match.group(1)
        args = event.pattern_match.group(2) or ""
        
        # 1. عرض قائمة المساعدة
        if cmd == "حماية":
            if not args:
                help_text = f"**{SECTION_NAME}**\n\n"
                for category, commands in COMMANDS.items():
                    help_text += f"**{category}:**\n"
                    help_text += "\n".join(commands) + "\n\n"
                help_text += "⚡ **للمساعدة في أمر محدد:** `.حماية [اسم القسم]`"
                await event.edit(help_text)
            else:
                category = args.strip()
                if category in COMMANDS:
                    text = f"**{category}:**\n\n"
                    text += "\n".join(COMMANDS[category])
                    await event.edit(text)
                else:
                    await event.edit("⚠️ **القسم غير موجود.**\n**الأقسام المتاحة:**\n" + ", ".join(COMMANDS.keys()))
        
        # 2. إدارة الحظر التلقائي
        elif cmd == "تفعيل" and "حظر" in args:
            manager.config["auto_block"]["enabled"] = True
            manager.save_config()
            await event.edit("🛡 **تم تفعيل الحظر التلقائي**\n📊 **الحد الأقصى:** {} رسائل خلال 60 ثانية".format(
                manager.config["auto_block"]["max_messages"]
            ))
        
        elif cmd == "تعطيل" and "حظر" in args:
            manager.config["auto_block"]["enabled"] = False
            manager.save_config()
            await event.edit("🔓 **تم تعطيل الحظر التلقائي**")
        
        elif cmd == "عدد" and args.startswith("الحظر"):
            try:
                num = int(args.split()[1])
                if 1 <= num <= 10:
                    manager.config["auto_block"]["max_messages"] = num
                    manager.save_config()
                    await event.edit(f"✅ **تم تحديد عدد الرسائل المسموحة إلى:** {num}")
                else:
                    await event.edit("⚠️ **الرجاء إدخال رقم بين 1 و 10**")
            except:
                await event.edit("❌ **استخدم:** `.عدد الحظر [رقم]`")
        
        elif cmd == "حظر" and "يدوي" in args:
            if event.reply_to_msg_id:
                reply = await event.get_reply_message()
                user_id = reply.sender_id
                username = reply.sender.username or "مستخدم"
            else:
                parts = args.split()
                if len(parts) > 1:
                    username = parts[1].replace("@", "")
                    try:
                        user = await event.client.get_entity(username)
                        user_id = user.id
                    except:
                        await event.edit("❌ **لم يتم العثور على المستخدم**")
                        return
                else:
                    await event.edit("❌ **استخدم:** `.حظر يدوي @معرف` أو رد على رسالة")
                    return
            
            if user_id not in manager.config["auto_block"]["blocked_users"]:
                manager.config["auto_block"]["blocked_users"].append(user_id)
                manager.update_stats("total_blocked")
                await event.client(functions.contacts.BlockRequest(user_id))
                await event.edit(f"⛔ **تم حظر** @{username}")
        
        elif cmd == "الغاء" and args.startswith("الحظر"):
            parts = args.split()
            if len(parts) > 1:
                username = parts[1].replace("@", "")
                try:
                    user = await event.client.get_entity(username)
                    user_id = user.id
                    if user_id in manager.config["auto_block"]["blocked_users"]:
                        manager.config["auto_block"]["blocked_users"].remove(user_id)
                        await event.client(functions.contacts.UnblockRequest(user_id))
                        await event.edit(f"✅ **تم إلغاء حظر** @{username}")
                    else:
                        await event.edit("⚠️ **المستخدم غير محظور**")
                except:
                    await event.edit("❌ **لم يتم العثور على المستخدم**")
        
        # 3. إدارة الرد التلقائي
        elif cmd == "تفعيل" and "الرد" in args:
            manager.config["auto_reply"]["enabled"] = True
            manager.save_config()
            await event.edit("✅ **تم تفعيل الرد التلقائي**\n⏰ **التأخير:** {} ثانية".format(
                manager.config["auto_reply"]["delay"]
            ))
        
        elif cmd == "تعطيل" and "الرد" in args:
            manager.config["auto_reply"]["enabled"] = False
            manager.save_config()
            await event.edit("❌ **تم تعطيل الرد التلقائي**")
        
        elif cmd == "وضع" and args.startswith("رد"):
            text = args[3:].strip()
            if text:
                manager.config["auto_reply"]["message"] = text
                manager.save_config()
                await event.edit(f"📝 **تم تحديث رسالة الرد:**\n`{text}`")
            else:
                await event.edit("❌ **استخدم:** `.وضع رد [نص]`")
        
        elif cmd == "وقت" and args.startswith("الرد"):
            try:
                delay = int(args.split()[1])
                if 0 <= delay <= 60:
                    manager.config["auto_reply"]["delay"] = delay
                    manager.save_config()
                    await event.edit(f"⏰ **تم ضبط وقت التأخير إلى:** {delay} ثانية")
                else:
                    await event.edit("⚠️ **الرجاء إدخال رقم بين 0 و 60**")
            except:
                await event.edit("❌ **استخدم:** `.وقت الرد [ثواني]`")
        
        # 4. إدارة وضع الشبح
        elif cmd == "شبح":
            if args == "للكل":
                manager.config["ghost_mode"]["for_all"] = True
                manager.save_config()
                await event.edit("👻 **تم تفعيل الشبح لجميع الدردشات**")
            elif args == "خاص":
                manager.config["ghost_mode"]["for_all"] = False
                manager.config["ghost_mode"]["for_private"] = True
                manager.save_config()
                await event.edit("👻 **تم تفعيل الشبح للخاص فقط**")
        
        elif cmd == "تفعيل" and "الشبح" in args:
            manager.config["ghost_mode"]["enabled"] = True
            manager.save_config()
            await event.edit("👻 **تم تفعيل وضع الشبح**\n👁‍🗨 **القراءة ستكون مخفية**")
        
        elif cmd == "تعطيل" and "الشبح" in args:
            manager.config["ghost_mode"]["enabled"] = False
            manager.save_config()
            await event.edit("👁‍🗨 **تم إيقاف وضع الشبح**")
        
        # 5. إدارة حفظ الميديا
        elif cmd == "تفعيل" and "الحفظ" in args:
            manager.config["auto_save"]["enabled"] = True
            manager.save_config()
            await event.edit("💾 **تم تفعيل حفظ الميديا ذاتية التدمير**\n📁 **المجلد:** `{}`".format(SAVE_DIR))
        
        elif cmd == "تعطيل" and "الحفظ" in args:
            manager.config["auto_save"]["enabled"] = False
            manager.save_config()
            await event.edit("🗑 **تم إيقاف الحفظ التلقائي**")
        
        elif cmd == "المحفوظات":
            files = os.listdir(SAVE_DIR)
            if files:
                text = "📁 **المحفوظات:**\n\n"
                for i, file in enumerate(files[:10], 1):
                    size = os.path.getsize(os.path.join(SAVE_DIR, file)) // 1024
                    text += f"{i}. `{file}` - {size} KB\n"
                if len(files) > 10:
                    text += f"\n📊 **و {len(files)-10} ملفات أخرى...**"
                await event.edit(text)
            else:
                await event.edit("📭 **لا توجد ملفات محفوظة**")
        
        elif cmd == "مسح" and "المحفوظات" in args:
            files = os.listdir(SAVE_DIR)
            count = 0
            for file in files:
                try:
                    os.remove(os.path.join(SAVE_DIR, file))
                    count += 1
                except:
                    pass
            manager.config["auto_save"]["saved_count"] = 0
            manager.save_config()
            await event.edit(f"🧹 **تم حذف {count} ملف**")
        
        # 6. الإحصائيات والمعلومات
        elif cmd == "احصائيات":
            stats = manager.config["stats"]
            config = manager.config
            
            text = "📊 **إحصائيات الحماية:**\n\n"
            text += f"👤 **المحظورين:** {stats['total_blocked']}\n"
            text += f"💬 **الردود التلقائية:** {stats['total_replied']}\n"
            text += f"💾 **الملفات المحفوظة:** {stats['total_saved']}\n"
            text += f"⏰ **آخر نشاط:** {stats['last_activity'] or 'لا يوجد'}\n\n"
            
            text += "⚙️ **الإعدادات الحالية:**\n"
            text += f"• الحظر التلقائي: {'✅' if config['auto_block']['enabled'] else '❌'}\n"
            text += f"• الرد التلقائي: {'✅' if config['auto_reply']['enabled'] else '❌'}\n"
            text += f"• وضع الشبح: {'✅' if config['ghost_mode']['enabled'] else '❌'}\n"
            text += f"• حفظ الميديا: {'✅' if config['auto_save']['enabled'] else '❌'}"
            
            await event.edit(text)
        
        elif cmd == "المحظورين":
            blocked = manager.config["auto_block"]["blocked_users"]
            if blocked:
                text = "⛔ **قائمة المحظورين:**\n\n"
                for i, user_id in enumerate(blocked[:15], 1):
                    text += f"{i}. `{user_id}`\n"
                if len(blocked) > 15:
                    text += f"\n📊 **و {len(blocked)-15} مستخدمين آخرين...**"
                await event.edit(text)
            else:
                await event.edit("✅ **لا يوجد مستخدمين محظورين**")
        
        elif cmd == "نسخة" and "احتياطية" in args:
            if manager.save_config():
                await event.edit("💾 **تم حفظ نسخة احتياطية من الإعدادات**")
            else:
                await event.edit("❌ **فشل في حفظ النسخة الاحتياطية**")
        
    except Exception as e:
        await event.edit(f"❌ **حدث خطأ:** `{str(e)}`")

# =========================================================
# 🛡 المحرك الخلفي - معالجة الرسائل الواردة
# =========================================================
@events.register(events.NewMessage(incoming=True))
async def incoming_protection_logic(event):
    try:
        if not event.is_private and not manager.config["ghost_mode"]["for_all"]:
            return
            
        sender = await event.get_sender()
        if not sender or sender.bot or sender.is_self:
            return
        
        uid = sender.id
        now = time.time()
        config = manager.config
        
        # 1. وضع الشبح (Ghost Mode)
        if config["ghost_mode"]["enabled"]:
            if (config["ghost_mode"]["for_all"] or 
                (config["ghost_mode"]["for_private"] and event.is_private)):
                await event.message.mark_read()
        
        # 2. التحقق من الحظر اليدوي
        if uid in config["auto_block"]["blocked_users"]:
            return
        
        # 3. حظر المتطفلين (Auto Block)
        if config["auto_block"]["enabled"] and event.is_private:
            if uid not in manager.flood_cache:
                manager.flood_cache[uid] = {'count': 1, 'time': now, 'warned': False}
            else:
                time_diff = now - manager.flood_cache[uid]['time']
                
                # إعادة التعيين بعد نافذة الوقت
                if time_diff > config["auto_block"]["time_window"]:
                    manager.flood_cache[uid] = {'count': 1, 'time': now, 'warned': False}
                else:
                    manager.flood_cache[uid]['count'] += 1
                
                # التحذير عند اقتراب الحد
                if (manager.flood_cache[uid]['count'] == config["auto_block"]["max_messages"] - 1 and 
                    not manager.flood_cache[uid]['warned']):
                    await event.reply("⚠️ **تحذير:** أنت على وشك الحظر!")
                    manager.flood_cache[uid]['warned'] = True
                
                # الحظر عند تجاوز الحد
                if manager.flood_cache[uid]['count'] >= config["auto_block"]["max_messages"]:
                    await event.reply(f"⛔ **تم حظرك تلقائياً لتجاوزك {config['auto_block']['max_messages']} رسائل خلال دقيقة.**")
                    config["auto_block"]["blocked_users"].append(uid)
                    manager.update_stats("total_blocked")
                    await event.client(functions.contacts.BlockRequest(uid))
                    
                    # حذف من الكاش
                    if uid in manager.flood_cache:
                        del manager.flood_cache[uid]
                    
                    manager.save_config()
                    return
        
        # 4. الرد التلقائي (Auto Reply)
        if (config["auto_reply"]["enabled"] and event.is_private and 
            uid not in config["auto_reply"]["exceptions"]):
            
            # التحقق من عدم وجود رد حديث
            cache_key = f"reply_{uid}"
            if cache_key not in manager.user_cache or now - manager.user_cache[cache_key] > 300:  # 5 دقائق
                await asyncio.sleep(config["auto_reply"]["delay"])
                
                # تنسيق الرسالة
                current_time = datetime.now().strftime("%I:%M %p")
                current_date = datetime.now().strftime("%Y/%m/%d")
                message = config["auto_reply"]["message"]
                message = message.replace("{time}", current_time)
                message = message.replace("{date}", current_date)
                message = message.replace("{name}", sender.first_name or "مستخدم")
                
                await event.reply(message)
                manager.user_cache[cache_key] = now
                manager.update_stats("total_replied")
        
        # 5. الحفظ التلقائي لميديا التدمير
        if config["auto_save"]["enabled"] and event.is_private and event.media:
            if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
                try:
                    # تنزيل الملف
                    path = await event.download_media(SAVE_DIR)
                    if path:
                        # تحديث الإحصائيات
                        config["auto_save"]["saved_count"] += 1
                        manager.update_stats("total_saved")
                        
                        # إرسال إشعار
                        if config["auto_save"]["notify"]:
                            filename = os.path.basename(path)
                            file_size = os.path.getsize(path) // 1024
                            
                            caption = (
                                f"💣 **تم حفظ ميديا مؤقتة**\n"
                                f"👤 **من:** {sender.first_name or 'مجهول'}\n"
                                f"📁 **الملف:** `{filename}`\n"
                                f"📊 **الحجم:** {file_size} KB\n"
                                f"⏰ **الوقت:** {datetime.now().strftime('%I:%M %p')}"
                            )
                            
                            await event.client.send_file(
                                'me', 
                                path, 
                                caption=caption
                            )
                except Exception as e:
                    print(f"Error saving media: {e}")
    
    except Exception as e:
        print(f"Protection error: {e}")

# =========================================================
# 🔄 دالة تنظيف الكاش التلقائي
# =========================================================
async def cleanup_cache():
    """تنظيف الكاش القديم تلقائياً"""
    while True:
        await asyncio.sleep(3600)  # كل ساعة
        try:
            now = time.time()
            # تنظيف flood_cache
            to_remove = []
            for uid, data in manager.flood_cache.items():
                if now - data['time'] > 3600:  # ساعة واحدة
                    to_remove.append(uid)
            
            for uid in to_remove:
                del manager.flood_cache[uid]
            
            # تنظيف user_cache (للردود)
            to_remove = []
            for key, timestamp in manager.user_cache.items():
                if now - timestamp > 86400:  # 24 ساعة
                    to_remove.append(key)
            
            for key in to_remove:
                del manager.user_cache[key]
                
        except:
            pass

# =========================================================
# 🚀 بدء النظام
# =========================================================
async def start_protection_system():
    """بدء تشغيل نظام الحماية"""
    print(f"✅ نظام الحماية يعمل ({SECTION_NAME})")
    print(f"📁 مجلد الحفظ: {os.path.abspath(SAVE_DIR)}")
    print(f"⚙️ الإعدادات: {CONFIG_FILE}")
    
    # بدء تنظيف الكاش
    asyncio.create_task(cleanup_cache())
