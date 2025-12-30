import os, asyncio, time, json
from telethon import events, functions, types
from datetime import datetime

# ==============================
# ⚙️ الإعدادات الأساسية
# ==============================
SAVE_DIR = "saved_media"
CONFIG_FILE = "protection_config.json"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==============================
# 📊 التخزين
# ==============================
class ProtectionStorage:
    def __init__(self):
        self.data = self.load()
        self.flood_cache = {}
    
    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "block": False,
            "block_limit": 3,
            "reply": False,
            "reply_text": "🚀 أنا مشغول الآن، سأرد عليك لاحقاً.",
            "ghost": False,
            "save": False,
            "blocked": [],
            "stats": {"blocks": 0, "replies": 0, "saves": 0}
        }
    
    def save(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.data, f)
        except:
            pass

storage = ProtectionStorage()

# ==============================
# 🔧 جميع الأوامر في مكان واحد
# ==============================
@events.register(events.NewMessage(outgoing=True, pattern=r"^\.(حماية|تفعيل الحظر|تعطيل الحظر|تفعيل الرد|تعطيل الرد|وضع رد|تفعيل الشبح|تعطيل الشبح|تفعيل الحفظ|تعطيل الحفظ|عدد الحظر|المحظورين|فك حظر|حظر|الاحصائيات)$"))
async def handle_all_commands(event):
    cmd = event.pattern_match.group(1)
    
    if cmd == "حماية":
        text = """🛡 **أوامر حماية التليثون:**
        
• `.تفعيل الحظر` - تشغيل منع المزعجين
• `.تعطيل الحظر` - إيقاف المنع
• `.عدد الحظر [رقم]` - تغيير عدد الرسائل (افتراضي 3)
• `.حظر @معرف` - حظر شخص يدوي
• `.المحظورين` - عرض المحظورين
• `.فك حظر @معرف` - إلغاء الحظر

• `.تفعيل الرد` - رد تلقائي في الخاص
• `.تعطيل الرد` - إيقاف الرد
• `.وضع رد [نص]` - تغيير الرسالة

• `.تفعيل الشبح` - إخفاء المشاهدة
• `.تعطيل الشبح` - إظهار المشاهدة

• `.تفعيل الحفظ` - حفظ الصور المتحلقة
• `.تعطيل الحفظ` - إيقاف الحفظ

• `.الاحصائيات` - إحصائيات النظام"""
        await event.edit(text)
    
    elif cmd == "تفعيل الحظر":
        storage.data["block"] = True
        storage.save()
        await event.edit("✅ **تم تشغيل الحظر التلقائي**")
    
    elif cmd == "تعطيل الحظر":
        storage.data["block"] = False
        storage.save()
        await event.edit("❌ **تم إيقاف الحظر التلقائي**")
    
    elif cmd == "تفعيل الرد":
        storage.data["reply"] = True
        storage.save()
        await event.edit("✅ **تم تفعيل الرد التلقائي**")
    
    elif cmd == "تعطيل الرد":
        storage.data["reply"] = False
        storage.save()
        await event.edit("❌ **تم إيقاف الرد التلقائي**")
    
    elif cmd == "تفعيل الشبح":
        storage.data["ghost"] = True
        storage.save()
        await event.edit("👻 **تم تفعيل وضع الشبح**")
    
    elif cmd == "تعطيل الشبح":
        storage.data["ghost"] = False
        storage.save()
        await event.edit("👁 **تم إيقاف وضع الشبح**")
    
    elif cmd == "تفعيل الحفظ":
        storage.data["save"] = True
        storage.save()
        await event.edit("💾 **تم تشغيل حفظ الصور المتحلقة**")
    
    elif cmd == "تعطيل الحفظ":
        storage.data["save"] = False
        storage.save()
        await event.edit("🗑 **تم إيقاف الحفظ التلقائي**")
    
    elif cmd == "المحظورين":
        if storage.data["blocked"]:
            text = "👥 **المحظورين:**\n"
            for user_id in storage.data["blocked"][:20]:
                text += f"• `{user_id}`\n"
            if len(storage.data["blocked"]) > 20:
                text += f"\n+ {len(storage.data['blocked']) - 20} أكثر..."
            await event.edit(text)
        else:
            await event.edit("✅ **لا يوجد محظورين**")
    
    elif cmd == "الاحصائيات":
        stats = storage.data["stats"]
        text = f"""📊 **إحصائيات الحماية:**
        
• الحظر التلقائي: {'✅' if storage.data['block'] else '❌'}
• الرد التلقائي: {'✅' if storage.data['reply'] else '❌'}
• وضع الشبح: {'✅' if storage.data['ghost'] else '❌'}
• الحفظ التلقائي: {'✅' if storage.data['save'] else '❌'}

📈 **النشاط:**
• تم حظر: {stats['blocks']} شخص
• تم الرد: {stats['replies']} مرة
• تم حفظ: {stats['saves']} ملف"""
        await event.edit(text)

@events.register(events.NewMessage(outgoing=True, pattern=r"^\.وضع رد (.*)"))
async def set_reply(event):
    text = event.pattern_match.group(1)
    storage.data["reply_text"] = text
    storage.save()
    await event.edit(f"📝 **تم تغيير رد التلقائي إلى:**\n`{text}`")

@events.register(events.NewMessage(outgoing=True, pattern=r"^\.عدد الحظر (\d+)"))
async def set_block_limit(event):
    num = int(event.pattern_match.group(1))
    if 1 <= num <= 10:
        storage.data["block_limit"] = num
        storage.save()
        await event.edit(f"🔢 **عدد الرسائل المسموحة:** {num}")
    else:
        await event.edit("⚠️ **اختر رقم بين 1 و 10**")

@events.register(events.NewMessage(outgoing=True, pattern=r"^\.حظر (@?\w+)"))
async def manual_block(event):
    user_input = event.pattern_match.group(1)
    
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
        try:
            user = await event.client.get_entity(user_id)
            username = user.username or "مستخدم"
        except:
            username = "مستخدم"
    else:
        try:
            user = await event.client.get_entity(user_input)
            user_id = user.id
            username = user.username or user_input
        except:
            await event.edit("❌ **لم أجد المستخدم**")
            return
    
    if user_id not in storage.data["blocked"]:
        storage.data["blocked"].append(user_id)
        storage.data["stats"]["blocks"] += 1
        storage.save()
        await event.client(functions.contacts.BlockRequest(user_id))
        await event.edit(f"⛔ **تم حظر** @{username}")
    else:
        await event.edit("⚠️ **المستخدم محظور بالفعل**")

@events.register(events.NewMessage(outgoing=True, pattern=r"^\.فك حظر (@?\w+)"))
async def manual_unblock(event):
    user_input = event.pattern_match.group(1)
    
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    else:
        try:
            user = await event.client.get_entity(user_input)
            user_id = user.id
        except:
            await event.edit("❌ **لم أجد المستخدم**")
            return
    
    if user_id in storage.data["blocked"]:
        storage.data["blocked"].remove(user_id)
        storage.save()
        await event.client(functions.contacts.UnblockRequest(user_id))
        await event.edit("✅ **تم فك الحظر**")
    else:
        await event.edit("⚠️ **المستخدم غير محظور**")

# ==============================
# 🛡 المحرك الأساسي
# ==============================
@events.register(events.NewMessage(incoming=True))
async def protection_core(event):
    try:
        if not event.is_private:
            return
        
        sender = await event.get_sender()
        if not sender or sender.bot or sender.is_self:
            return
        
        user_id = sender.id
        
        # 1. التحقق من الحظر اليدوي
        if user_id in storage.data["blocked"]:
            return
        
        # 2. وضع الشبح
        if storage.data["ghost"]:
            await event.message.mark_read()
        
        # 3. الحظر التلقائي
        if storage.data["block"]:
            now = time.time()
            if user_id not in storage.flood_cache:
                storage.flood_cache[user_id] = {'count': 1, 'time': now}
            else:
                if now - storage.flood_cache[user_id]['time'] > 60:
                    storage.flood_cache[user_id] = {'count': 1, 'time': now}
                else:
                    storage.flood_cache[user_id]['count'] += 1
                
                if storage.flood_cache[user_id]['count'] >= storage.data["block_limit"]:
                    await event.reply("🚫 **تم حظرك بسبب التكرار**")
                    storage.data["blocked"].append(user_id)
                    storage.data["stats"]["blocks"] += 1
                    storage.save()
                    await event.client(functions.contacts.BlockRequest(user_id))
                    if user_id in storage.flood_cache:
                        del storage.flood_cache[user_id]
                    return
        
        # 4. الرد التلقائي
        if storage.data["reply"]:
            if user_id not in storage.flood_cache or storage.flood_cache[user_id]['count'] == 1:
                await asyncio.sleep(1)
                await event.reply(storage.data["reply_text"])
                storage.data["stats"]["replies"] += 1
                storage.save()
        
        # 5. حفظ الوسائط
        if storage.data["save"] and event.media:
            if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
                try:
                    path = await event.download_media(SAVE_DIR)
                    if path:
                        storage.data["stats"]["saves"] += 1
                        storage.save()
                        await event.client.send_file(
                            'me', 
                            path, 
                            caption=f"💾 **تم حفظ ملف من:** {sender.first_name}"
                        )
                        os.remove(path)
                except:
                    pass
                    
    except Exception as e:
        print(f"خطأ في الحماية: {e}")

# ==============================
# 🧹 تنظيف الكاش
# ==============================
async def clean_cache():
    while True:
        await asyncio.sleep(300)
        try:
            now = time.time()
            to_remove = []
            for user_id, data in storage.flood_cache.items():
                if now - data['time'] > 300:
                    to_remove.append(user_id)
            for user_id in to_remove:
                del storage.flood_cache[user_id]
        except:
            pass

# ==============================
# 🚀 بدء النظام
# ==============================
async def start_protection():
    print("✅ نظام الحماية يعمل بنجاح!")
    print("📁 مجلد الحفظ:", os.path.abspath(SAVE_DIR))
    print("⚙️ ملف الإعدادات:", CONFIG_FILE)
    print("📞 استخدم .حماية لعرض الأوامر")
    asyncio.create_task(clean_cache())

# ابدأ النظام عند الاستيراد
# في ملفك الرئيسي أضف: await start_protection()
