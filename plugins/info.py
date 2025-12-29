from telethon import events
from datetime import datetime
from __main__ import client # استيراد العميل من المحرك الأساسي

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "👤 قـسـم الـمـعـلـومـات"
COMMANDS = "• `.معلوماتي` : لـجـلـب بـيـانـات حـسـابـك الـكـامـلـة\n• `.الزمن` : لـعـرض الـتـوقـيـت الـحـالـي بدقـة"

@client.on(events.NewMessage(outgoing=True, pattern=r'\.معلوماتي'))
async def info_handler(event):
    await event.edit("🔍 **جـارِ جـلـب بـيـانـات الـحـسـاب...**")
    
    # جلب معلومات المستخدم
    me = await event.client.get_me()
    username = f"@{me.username}" if me.username else "لا يوجد"
    user_id = me.id
    first_name = me.first_name
    last_name = me.last_name if me.last_name else ""
    
    # تنسيق الرسالة بشكل "مفول"
    info_text = (
        "╔════════════════════╗\n"
        "      **👤 مـعـلـومـات الـبـروفـايـل**\n"
        "╚════════════════════╝\n\n"
        f"🙋‍♂️ **الاسـم:** {first_name} {last_name}\n"
        f"🆔 **الآيـدي:** `{user_id}`\n"
        f"🔗 **الـيـوزر:** {username}\n"
        f"📱 **الـرقـم:** مـخـفـي لحـمـايـتـك\n"
        "───━━━━─ ● ─━━━━───\n"
        f"📅 **الـتـاريخ:** {datetime.now().strftime('%Y-%m-%d')}\n"
        f"⏰ **الـوقـت:** {datetime.now().strftime('%H:%M:%S')}\n"
        "───━━━━─ ● ─━━━━───\n"
        "💎 **S O U R C E  C O M M O N**"
    )
    
    await event.edit(info_text)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.الزمن'))
async def time_handler(event):
    curr_time = datetime.now().strftime("%H:%M:%S")
    await event.edit(f"🕒 **الـوقـت الـحـالـي الآن:** `{curr_time}`")
