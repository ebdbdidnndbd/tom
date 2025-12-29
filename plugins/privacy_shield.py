# plugins/global_tools.py
import os
import asyncio
from telethon import events, types

# --- كليشة المساعدة (تظهر في .الاوامر) ---
SECTION_NAME = "🛡️ المنظومة العالمية"
COMMANDS = (
    "`.حفظ` [تفعيل/تعطيل] - لخزن رسائل المجموعات\n"
    "`.صيد` [تفعيل/تعطيل] - لصيد المحذوفات والتدمير\n"
    "`.فحص` - للتأكد من استجابة الأمر"
)

# نظام حفظ الحالة (States) لضمان عدم التضارب
SETTINGS = {"save_groups": False, "anti_delete": False}

# 1. أمر الفحص (Ping) للتأكد من الربط
@events.register(events.NewMessage(outgoing=True, pattern=r"\.فحص"))
async def ping_handler(event):
    await event.edit("⚡ **الأمر يعمل بنجاح!**\n📡 تم ربط الملحق بالمحرك العالمي.")

# 2. أمر التحكم بنظام الحفظ والصيد
@events.register(events.NewMessage(outgoing=True, pattern=r"\.(حفظ|صيد) (تفعيل|تعطيل)"))
async def toggle_handler(event):
    cmd = event.pattern_match.group(1)
    status = event.pattern_match.group(2)
    
    is_on = True if status == "تفعيل" else False
    
    if cmd == "حفظ":
        SETTINGS["save_groups"] = is_on
        word = "✅ تم تفعيل" if is_on else "🛑 تم تعطيل"
        await event.edit(f"{word} **خزن رسائل المجموعات.**")
    
    elif cmd == "صيد":
        SETTINGS["anti_delete"] = is_on
        word = "✅ تم تفعيل" if is_on else "🛑 تم تعطيل"
        await event.edit(f"{word} **صائد المحذوفات والتدمير الذاتي.**")

# 3. المحرك الخلفي (الذي ينفذ المهام تلقائياً)
@events.register(events.NewMessage(incoming=True))
async def global_sniffer(event):
    """هذا الجزء هو الذي يقوم بالعمل الحقيقي في الخلفية"""
    
    # أولاً: صيد التدمير الذاتي (الصور والفيديوهات التي تختفي)
    if SETTINGS["anti_delete"]:
        if event.media and hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds:
            try:
                # الحفظ الفوري في الرسائل المحفوظة (me) لضمان الخصوصية
                await event.forward_to("me")
            except: pass

    # ثانياً: خزن رسائل المجموعات (إذا كان مفعلاً)
    if SETTINGS["save_groups"] and event.is_group:
        try:
            # التوجيه التلقائي للمخزن
            await event.forward_to("me")
        except: pass

# ملاحظة برمجية: تأكد أن المحرك (main.py) يحتوي على client.add_event_handler
