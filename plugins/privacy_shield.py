# plugins/privacy_shield.py
import os
from telethon import events, types

# تعريفات القائمة للمحرك
SECTION_NAME = "🛡️ حماية الخصوصية"
COMMANDS = "`.تفعيل_الصيد` - تفعيل كاش الرسائل المحذوفة\n`.كاش` - عرض عدد الرسائل في الذاكرة"

# حالة النظام
IS_SNIFFING = True

async def setup(client, cache):
    @client.on(events.NewMessage(incoming=True))
    async def cache_handler(event):
        """حفظ الرسائل في الكاش فور وصولها لصيدها إذا حُذفت"""
        if IS_SNIFFING and event.text:
            cache[event.id] = {
                'text': event.text,
                'sender': event.sender_id,
                'chat': event.chat_id
            }
            # تنظيف الكاش القديم (أول 1000 رسالة فقط)
            if len(cache) > 1000:
                key_to_del = next(iter(cache))
                del cache[key_to_del]

    @client.on(events.MessageDeleted)
    async def deleted_log_handler(event):
        """صيد الرسائل المحذوفة وإرسالها لمخزنك الخاص"""
        for msg_id in event.deleted_ids:
            if msg_id in cache:
                msg_data = cache[msg_id]
                log_text = (
                    f"👀 **تم رصد حذف رسالة!**\n"
                    f"👤 **المرسل:** `{msg_data['sender']}`\n"
                    f"💬 **المحتوى:** {msg_data['text']}"
                )
                # إرسال إلى الرسائل المحفوظة (me)
                await client.send_message("me", log_text)
                del cache[msg_id]

    @client.on(events.Raw(types.UpdateServiceNotification))
    async def screenshot_handler(update):
        """كشف تصوير الشاشة في المحادثات الخاصة"""
        if "screenshot" in update.message.lower():
            await client.send_message("me", "⚠️ **تنبيه أمني:** قام الطرف الآخر بتصوير الشاشة!")

    print("🛡️ إضافة 'حامي الخصوصية' جاهزة للعمل بنسبة 100%")
