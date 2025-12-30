import time
from telethon import events
from __main__ import client # استيراد العميل من ملف main ا

@client.on(events.NewMessage(outgoing=True, pattern=r'\.فحص'))
async def ping_handler(event):
    # حساب وقت البداية
    start = time.time()
    
    # رسالة مؤقتة للفحص
    await event.edit("🚀 **جـارِ فـحـص الاسـتـجـابـة...**")
    
    # حساب وقت النهاية وتحويله لميلي ثانية
    end = time.time()
    ms = round((end - start) * 1000, 2)
    
    # عرض النتيجة النهائية بشكل احترافي
    result_text = (
        f"📶 **سـورس كـومـن يـعـمـل بـكـفـاءة!**\n\n"
        f"⚡ **الاسـتـجـابـة:** `{ms}ms`\n"
        f"👤 **الـمـطـور:** @iomk0\n"
        f"📢 **الـقـنـاة:** @iomk3"
    )
    
    await event.edit(result_text)
