import asyncio
from datetime import datetime, timedelta
from telethon import events, functions

# --- بيانات القسم (تظهر فقط عند طلب .م3) ---
SECTION_NAME = "⏰ قسم الوقت والبروفايل (م3)"
HELP_TEXT = (
    "**⏰ قائمة أوامر الوقت والبروفايل:**\n\n"
    "`.الساعة` ➖ تشغيل/إيقاف الوقت في الاسم\n"
    "`.اسم متحرك` ➖ تشغيل/إيقاف الزخرفة المتحركة\n"
    "`.تاج` ➖ وضع التاج الملكي 👑 لاسمك\n"
    "`.ضع اسم [النص]` ➖ تغيير اسمك فوراً\n"
    "`.ضع بايو [النص]` ➖ تغيير نبذة الحساب\n"
    "`.زخرفة [النص]` ➖ زخرفة احترافية للنص"
)

# متغيرات الحالة (مخفية داخل الملف)
state = {"clock": False, "anim": False}

def make_wide(text):
    """تحويل الأرقام لخط عريض للساعة"""
    mapping = str.maketrans("0123456789:", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗꞉")
    return text.translate(mapping)

# =========================================================
# 🛠️ المحرك الموحد (يستقبل كل أوامر القسم)
# =========================================================

@events.register(events.NewMessage(outgoing=True, pattern=r"^\.(م3|الساعة|اسم متحرك|تاج|ضع اسم|ضع بايو|زخرفة)(.*)"))
async def profile_engine(event):
    cmd = event.pattern_match.group(1)
    args = event.pattern_match.group(2).strip()
    client = event.client

    # 1. عرض قائمة القسم فقط
    if cmd == "م3":
        await event.edit(f"**{SECTION_NAME}**\n\n{HELP_TEXT}\n\n👨‍💻 @iomk0")

    # 2. أمر التاج 👑
    elif cmd == "تاج":
        me = await client.get_me()
        name = me.first_name.replace("👑", "").strip()
        await client(functions.account.UpdateProfileRequest(first_name=f"👑 {name} 👑"))
        await event.edit("✅ **تم تفعيل التاج الملكي بنجاح.**")

    # 3. تغيير الاسم والبايو
    elif cmd == "ضع اسم" and args:
        await client(functions.account.UpdateProfileRequest(first_name=args))
        await event.edit(f"✅ **تم تغيير الاسم إلى:** {args}")
        
    elif cmd == "ضع بايو" and args:
        await client(functions.account.UpdateProfileRequest(about=args))
        await event.edit("✅ **تم تحديث النبذة بنجاح.**")

    # 4. الزخرفة الاحترافية
    elif cmd == "زخرفة" and args:
        fonts = [f"『 {args} 』", f"☬ {args} ☬", f"《 {args} 》", f"〔 {args} 〕"]
        await event.edit(f"✨ **الزخارف:**\n\n" + "\n".join(fonts))

    # 5. تشغيل الساعة (وقت العراق UTC+3)
    elif cmd == "الساعة":
        state["clock"] = not state["clock"]
        status = "تشغيل" if state["clock"] else "إيقاف"
        await event.edit(f"⏰ **تم {status} الساعة التلقائية في الاسم.**")
        if state["clock"]:
            asyncio.create_task(clock_worker(client))

    # 6. تشغيل الاسم المتحرك
    elif cmd == "اسم متحرك":
        state["anim"] = not state["anim"]
        status = "تشغيل" if state["anim"] else "إيقاف"
        await event.edit(f"✨ **تم {status} الاسم المتحرك بنجاح.**")
        if state["anim"]:
            asyncio.create_task(anim_worker(client))

# =========================================================
# 🔄 محركات الخلفية (بذات برمجة سورسك)
# =========================================================

async def clock_worker(client):
    """تحديث الساعة كل دقيقة"""
    while state["clock"]:
        try:
            now = datetime.utcnow() + timedelta(hours=3) # توقيت العراق
            wide_time = make_wide(now.strftime("%I:%M"))
            me = await client.get_me()
            base = me.first_name.split()[0] if me.first_name else "User"
            if wide_time not in me.first_name:
                await client(functions.account.UpdateProfileRequest(first_name=f"{base} {wide_time}"))
            await asyncio.sleep(60)
        except: await asyncio.sleep(60)

async def anim_worker(client):
    """تحديث زخرفة الاسم كل ثانيتين"""
    i = 0
    while state["anim"]:
        try:
            me = await client.get_me()
            base = me.first_name.split()[0] if me.first_name else "User"
            names = [base, f"✨ {base}", f"⚡ {base}", f"🔥 {base} 🔥", f"👑 {base}"]
            await client(functions.account.UpdateProfileRequest(first_name=names[i % len(names)]))
            i += 1
            await asyncio.sleep(2)
        except: await asyncio.sleep(5)
