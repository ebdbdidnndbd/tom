import time
import platform
from datetime import datetime
from telethon import events, functions, types
from __main__ import client, PLUGINS_HELP # استيراد العميل والقائمة

# --- بيانات القسم للوحة الأوامر التلقائية ---
SECTION_NAME = "🖥️ لـوحـة الـتـحـكـم Pro"
COMMANDS = "• `.لوحة` : عـرض إحـصـائـيـات الـحـسـاب والـنـظـام بـالـكـامـل"

# تسجيل وقت تشغيل السورس لحساب الـ Uptime
START_TIME = datetime.now()

@client.on(events.NewMessage(outgoing=True, pattern=r'\.لوحة'))
async def dashboard_handler(event):
    await event.edit("📊 **جـارِ تـحـلـيـل بـيـانـات الـمـحـرك والـحـسـاب...**")
    
    # 1. حساب مدة التشغيل (Uptime)
    uptime = datetime.now() - START_TIME
    days = uptime.days
    hours, rem = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    
    # 2. جلب إحصائيات المحادثات
    result = await event.client(functions.messages.GetDialogFiltersRequest())
    dialogs = await event.client.get_dialogs()
    
    private_chats = 0
    groups = 0
    channels = 0
    
    for dialog in dialogs:
        if dialog.is_user: private_chats += 1
        elif dialog.is_group: groups += 1
        elif dialog.is_channel: channels += 1

    # 3. جلب معلومات النظام
    py_version = platform.python_version()
    
    # تنسيق اللوحة بشكل احترافي
    dashboard_text = (
        "╔════════════════════╗\n"
        "      **💎 C O M M O N  -  D A S H B O A R D**\n"
        "╚════════════════════╝\n\n"
        f"⏳ **مـدة الـتـشـغـيـل:** `{days}d {hours}h {minutes}m`\n"
        f"⚙️ **إصـدار بـايـثـون:** `{py_version}`\n"
        "───━━━━─ ● ─━━━━───\n"
        "📊 **إحـصـائـيـات الـمـحـادثات:**\n"
        f"👤 **خـاص:** `{private_chats}`\n"
        f"👥 **مـجـمـوعـات:** `{groups}`\n"
        f"📢 **قـنـوات:** `{channels}`\n"
        "───━━━━─ ● ─━━━━───\n"
        "🛡️ **الـحـالـة:** مـتـصـل (جـلـسـة ثابتـة)\n"
        f"📅 **الـتـاريـخ:** `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
        "✨ **تـم الـتـحـلـيـل بـنـجـاح بـواسطـة Common Pro**"
    )
    
    await event.edit(dashboard_text)
