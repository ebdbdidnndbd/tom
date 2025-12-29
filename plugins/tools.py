from telethon import events
from __main__ import client

# البيانات التي يقرأها المحرك تلقائياً
SECTION_NAME = "🛠️ قـسـم الأدوات الـذكـيـة"
COMMANDS = (
    "• `.فحص` : لـقـيـاس سـرعـة الـمـحـرك\n"
    "• `.ايدي` : لـجـلـب مـعـلـومـات الـحـسـاب"
)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ايدي'))
async def get_id(event):
    me = await event.client.get_me()
    await event.edit(f"👤 **اسـمـك:** {me.first_name}\n🆔 **آيـدي الحـسـاب:** `{me.id}`")
