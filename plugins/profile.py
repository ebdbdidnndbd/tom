import asyncio
from datetime import datetime, timedelta
from telethon import events, functions

# --- تعريف القسم الرئيسي والوحيد ---
SECTION_NAME = "⏰ قسم الوقت والبروفايل (م3)"

# هذه القائمة تظهر فقط داخل هذا الأمر ولا تظهر في القائمة العامة
SUB_COMMANDS_HELP = (
    "`.م3` ➖ عرض هذه الواجهة\n"
    "`.الساعة` ➖ تشغيل الوقت التلقائي في الاسم\n"
    "`.اسم متحرك` ➖ تشغيل الزخرفة المتحركة\n"
    "`.تاج` ➖ وضع التاج الملكي 👑\n"
    "`.ضع اسم` / `.ضع بايو` ➖ تحديث بيانات الحساب\n"
    "`.زخرفة [النص]` ➖ زخرفة احترافية"
)

def make_wide(text):
    """تحويل أرقام الساعة لخط عريض"""
    mapping = str.maketrans("0123456789:", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗꞉")
    return text.translate(mapping)

# =========================================================
# 🛠️ المحرك المدمج (كل الأوامر داخل هذا الـ Handler)
# =========================================================

@events.register(events.NewMessage(outgoing=True, pattern=r"\.(م3|الساعة|اسم متحرك|تاج|ضع اسم|ضع بايو|زخرفة)(.*)"))
async def profile_engine(event):
    cmd = event.pattern_match.group(1)
    args = event.pattern_match.group(2).strip()
    
    # 1. عرض الواجهة (م3)
    if cmd == "م3":
        await event.edit(f"**{SECTION_NAME}:**\n\n{SUB_COMMANDS_HELP}\n\n👨‍💻 @iomk0")

    # 2. أمر التاج 👑
    elif cmd == "تاج":
        me = await event.client.get_me()
        name = me.first_name.replace("👑", "").strip()
        await event.client(functions.account.UpdateProfileRequest(first_name=f"👑 {name} 👑"))
        await event.edit("✅ **تم تفعيل التاج الملكي.**")

    # 3. تغيير الاسم والبايو
    elif cmd == "ضع اسم" and args:
        await event.client(functions.account.UpdateProfileRequest(first_name=args))
        await event.edit(f"✅ **تم تغيير الاسم إلى:** {args}")
        
    elif cmd == "ضع بايو" and args:
        await event.client(functions.account.UpdateProfileRequest(about=args))
        await event.edit("✅ **تم تحديث النبذة.**")

    # 4. الزخرفة
    elif cmd == "زخرفة" and args:
        fonts = [f"『 {args} 』", f"☬ {args} ☬", f"《 {args} 》"]
        await event.edit(f"✨ **الزخرفة:**\n" + "\n".join(fonts))

    # 5. تنبيه للوظائف التلقائية (الساعة والاسم المتحرك)
    elif cmd in ["الساعة", "اسم متحرك"]:
        await event.edit(f"⚙️ **تم إرسال أمر ({cmd}) للمحرك التلقائي...**")
