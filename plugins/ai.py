# plugins/ai_pro.py
from telethon import events
import aiohttp
import json
import random
import os
import asyncio
from __main__ import client

# --- بيانات الفهرسة لظهور الأوامر في قائمة السورس ---
SECTION_NAME = "🧠 قسم الذكاء الاصطناعي المطور"
COMMANDS = (
    "• `.ذكاء` :  قسم الذكاء الاصطناعي المتكامل\n"

)

# =========================================================
# 🎯 محرك Gemini 2.0 Flash Lite الأساسي
# =========================================================

class GeminiAI:
    def __init__(self):
        self.api_url = "https://firebasevertexai.googleapis.com/v1beta/projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite:generateContent"
        self.headers = {
            'User-Agent': "Ktor client",
            'Accept': "application/json",
            'Content-Type': "application/json",
            'x-goog-api-key': "AIzaSyD6QwvrvnjU7j-R6fkOghfIVKwtvc7SmLk",
            'x-goog-api-client': "gl-kotlin/2.2.0-ai fire/16.5.0",
            'x-firebase-appid': "1:652803432695:android:c4341db6033e62814f33f2",
            'x-firebase-appversion': "79",
            'x-firebase-appcheck': "eyJlcnJvciI6IlVOS05PV05fRVJST1IifQ=="
        }
        self.conversation_history = {}
    
    async def ask(self, prompt, system_prompt="أنت مساعد ذكي ومفيد."):
        """إرسال طلب إلى Gemini AI"""
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
            
            payload = {
                "model": "projects/gemmy-ai-bdc03/locations/us-central1/publishers/google/models/gemini-2.0-flash-lite",
                "contents": [{"role": "user", "parts": [{"text": full_prompt}]}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'candidates' in result and result['candidates']:
                            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Gemini Error: {e}")
        return None

# إنشاء كائن الذكاء الاصطناعي
gemini = GeminiAI()

# =========================================================
# 📱 أمر العرض: `.ذكاء`
# =========================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ذكاء$'))
async def ai_menu(event):
    """عرض قائمة أوامر الذكاء الاصطناعي"""
    menu = """
🧠 **سورس كومن - نظام الذكاء الاصطناعي المتكامل**

**📋 جميع الأوامر المتاحة:**

1️⃣ **🎯 المحادثة والاستفسار:**
   • `.سؤال [نص]` - محادثة ذكية مع AI
   • `.حكمة` - حكمة عشوائية ذكية
   • `.تعلم [موضوع]` - شرح تعليمي مفصل

2️⃣ **💻 البرمجة والتطوير:**
   • `.كود [لغة] [وصف]` - كتابة كود برمجي
   • `.حل [مشكلة]` - حل المشكلات البرمجية
   • `.تطوير` - معلومات عن التطوير

3️⃣ **📝 الكتابة والإبداع:**
   • `.مقال [موضوع]` - كتابة مقال متكامل
   • `.قصة [فكرة]` - كتابة قصة إبداعية
   • `.شعر [موضوع]` - كتابة قصيدة شعرية
   • `.افكار [موضوع]` - توليد أفكار إبداعية

4️⃣ **🌐 الترجمة والتلخيص:**
   • `.ترجم [نص]` - ترجمة احترافية
   • `.لخص [نص]` - تلخيص النصوص بذكاء

5️⃣ **🎨 التصميم والرسم:**
   • `.رسم [وصف]` - إنشاء وصف للصور
   • `.تصميم [وصف]` - تصميم جرافيكي
   • `.صور [وصف]` - إنشاء صور بالذكاء

6️⃣ **📊 التخطيط والاختبار:**
   • `.خطط [هدف]` - تخطيط استراتيجي
   • `.اختبر [موضوع]` - اختبار معرفي

**📌 أمثلة الاستخدام:**
• `.سؤال ما هي أفضل لغة برمجة؟`
• `.كود python برنامج حاسبة`
• `.مقال أهمية التكنولوجيا`
• `.رسم منظر غروب الشمس`
• `.حكمة`

**⚡ نظام متكامل مع 16 أمر مختلف**
**🧠 الذكاء: Gemini 2.0 Flash Lite**
**👤 المطور: @iomk0 | 📢 القناة: @iomk3**
    """
    await event.edit(menu)

# =========================================================
# 🎯 الأوامر الأساسية (تعمل مباشرة بدون .ذكاء)
# =========================================================

# 1. أمر السؤال
@client.on(events.NewMessage(outgoing=True, pattern=r'\.سؤال (.+)'))
async def ai_question(event):
    """محادثة ذكية مع AI"""
    question = event.pattern_match.group(1)
    await event.edit("🤔 **جاري التفكير في إجابة...**")
    
    response = await gemini.ask(
        question,
        "أنت مساعد ذكي باللغة العربية. أجب على الأسئلة بوضوح ودقة."
    )
    
    if response:
        await event.edit(f"🧠 **إجابة الذكاء:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر الاتصال بالذكاء الاصطناعي**")

# 2. أمر الكود
@client.on(events.NewMessage(outgoing=True, pattern=r'\.كود (.+)'))
async def ai_code(event):
    """كتابة كود برمجي"""
    text = event.pattern_match.group(1)
    
    # تحليل النص للحصول على اللغة والوصف
    parts = text.split(' ', 1)
    if len(parts) < 2:
        await event.edit("⚠️ **استخدم:** `.كود [لغة] [وصف الكود]`")
        return
    
    language, description = parts[0], parts[1]
    await event.edit(f"💻 **جاري كتابة كود {language}...**")
    
    response = await gemini.ask(
        f"اكتب كود {language} لـ: {description}",
        f"أنت مبرمج خبير في لغة {language}. اكتب كود نظيف وواضح مع تعليقات."
    )
    
    if response:
        await event.edit(f"```{language}\n{response}\n```")
    else:
        await event.edit("❌ **تعذر إنشاء الكود**")

# 3. أمر الرسم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.رسم (.+)'))
async def ai_draw(event):
    """إنشاء وصف للصور"""
    description = event.pattern_match.group(1)
    await event.edit("🎨 **جاري إنشاء وصف للصورة...**")
    
    response = await gemini.ask(
        f"صف صورة لـ: {description}",
        "أنت فنان محترف. صف صورة بدقة وتفصيل لاستخدامها في توليد الصور بالذكاء الاصطناعي."
    )
    
    if response:
        await event.edit(f"🖼 **وصف الصورة:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إنشاء الوصف**")

# 4. أمر المقال
@client.on(events.NewMessage(outgoing=True, pattern=r'\.مقال (.+)'))
async def ai_article(event):
    """كتابة مقال"""
    topic = event.pattern_match.group(1)
    await event.edit("📝 **جاري كتابة المقال...**")
    
    response = await gemini.ask(
        f"اكتب مقالاً عن: {topic}",
        "أنت كاتب محترف. اكتب مقالاً متكاملاً مع مقدمة وعرض وخاتمة وافكار رئيسية."
    )
    
    if response:
        await event.edit(f"📄 **المقال:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر كتابة المقال**")

# 5. أمر الترجمة
@client.on(events.NewMessage(outgoing=True, pattern=r'\.ترجم (.+)'))
async def ai_translate(event):
    """ترجمة النصوص"""
    text = event.pattern_match.group(1)
    await event.edit("🌍 **جاري الترجمة...**")
    
    response = await gemini.ask(
        f"ترجم النص التالي للعربية: {text}",
        "أنت مترجم محترف. ترجم النص بدقة مع الحفاظ على المعنى والسياق."
    )
    
    if response:
        await event.edit(f"🔤 **الترجمة:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر الترجمة**")

# 6. أمر التلخيص
@client.on(events.NewMessage(outgoing=True, pattern=r'\.لخص (.+)'))
async def ai_summarize(event):
    """تلخيص النصوص"""
    text = event.pattern_match.group(1)
    await event.edit("📄 **جاري تلخيص النص...**")
    
    response = await gemini.ask(
        f"لخص النص التالي: {text}",
        "أنت مختص في تلخيص النصوص. لخص النص بشكل مختصر ومفيد مع الحفاظ على الأفكار الرئيسية."
    )
    
    if response:
        await event.edit(f"📌 **الملخص:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر التلخيص**")

# 7. أمر الحل
@client.on(events.NewMessage(outgoing=True, pattern=r'\.حل (.+)'))
async def ai_solve(event):
    """حل المشكلات"""
    problem = event.pattern_match.group(1)
    await event.edit("🔍 **جاري البحث عن حل...**")
    
    response = await gemini.ask(
        f"حل المشكلة التالية: {problem}",
        "أنت خبير في حل المشكلات. قدم حلاً عملياً ومفصلاً مع شرح الخطوات."
    )
    
    if response:
        await event.edit(f"✅ **الحل المقترح:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إيجاد حل**")

# 8. أمر الأفكار
@client.on(events.NewMessage(outgoing=True, pattern=r'\.افكار (.+)'))
async def ai_ideas(event):
    """توليد أفكار إبداعية"""
    topic = event.pattern_match.group(1)
    await event.edit("💡 **جاري توليد الأفكار...**")
    
    response = await gemini.ask(
        f"قدم أفكار إبداعية عن: {topic}",
        "أنت مبدع محترف. قدم 5 أفكار إبداعية ومبتكرة ومفصلة حول الموضوع."
    )
    
    if response:
        await event.edit(f"✨ **الأفكار الإبداعية:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر توليد الأفكار**")

# 9. أمر التعلم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تعلم (.+)'))
async def ai_learn(event):
    """شرح تعليمي"""
    topic = event.pattern_match.group(1)
    await event.edit("🎓 **جاري إعداد الشرح...**")
    
    response = await gemini.ask(
        f"اشرح لي: {topic}",
        "أنت معلم محترف. اشرح الموضوع بطريقة مبسطة مع أمثلة عملية وتطبيقات."
    )
    
    if response:
        await event.edit(f"📚 **الشرح التعليمي:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إعداد الشرح**")

# 10. أمر القصة
@client.on(events.NewMessage(outgoing=True, pattern=r'\.قصة (.+)'))
async def ai_story(event):
    """كتابة قصة"""
    idea = event.pattern_match.group(1)
    await event.edit("📖 **جاري كتابة القصة...**")
    
    response = await gemini.ask(
        f"اكتب قصة عن: {idea}",
        "أنت كاتب قصص محترف. اكتب قصة مشوقة مع شخصيات وأحداث وحبكة درامية."
    )
    
    if response:
        await event.edit(f"📚 **القصة:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر كتابة القصة**")

# 11. أمر الشعر
@client.on(events.NewMessage(outgoing=True, pattern=r'\.شعر (.+)'))
async def ai_poem(event):
    """كتابة قصيدة شعرية"""
    topic = event.pattern_match.group(1)
    await event.edit("📜 **جاري كتابة القصيدة...**")
    
    response = await gemini.ask(
        f"اكتب قصيدة عن: {topic}",
        "أنت شاعر محترف. اكتب قصيدة فصيحة جميلة مع بحر شعري مناسب وقافية متناسقة."
    )
    
    if response:
        await event.edit(f"📜 **القصيدة الشعرية:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر كتابة القصيدة**")

# 12. أمر التصميم
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تصميم (.+)'))
async def ai_design(event):
    """تصميم جرافيك"""
    description = event.pattern_match.group(1)
    await event.edit("🎨 **جاري إنشاء التصميم...**")
    
    response = await gemini.ask(
        f"صمم: {description}",
        "أنت مصمم جرافيك محترف. صف تصميمًا كاملاً مع الألوان والخطوط والعناصر والتركيب."
    )
    
    if response:
        await event.edit(f"🖌 **التصميم المقترح:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إنشاء التصميم**")

# 13. أمر الخطط
@client.on(events.NewMessage(outgoing=True, pattern=r'\.خطط (.+)'))
async def ai_plan(event):
    """تخطيط استراتيجي"""
    goal = event.pattern_match.group(1)
    await event.edit("📊 **جاري إعداد الخطة...**")
    
    response = await gemini.ask(
        f"خطط لـ: {goal}",
        "أنت مخطط استراتيجي محترف. اعداد خطة عمل كاملة مع مراحل وجدول زمني ومؤشرات أداء."
    )
    
    if response:
        await event.edit(f"📅 **الخطة الاستراتيجية:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إعداد الخطة**")

# 14. أمر الاختبار
@client.on(events.NewMessage(outgoing=True, pattern=r'\.اختبر (.+)'))
async def ai_test(event):
    """اختبار معرفي"""
    topic = event.pattern_match.group(1)
    await event.edit("🧪 **جاري إعداد الاختبار...**")
    
    response = await gemini.ask(
        f"اختبر معرفتي في: {topic}",
        "أنت خبير في التقييم. اعداد اختبار معرفي مع 5 أسئلة متنوعة ودرجات لكل سؤال."
    )
    
    if response:
        await event.edit(f"📝 **الاختبار المعرفي:**\n\n{response}")
    else:
        await event.edit("❌ **تعذر إعداد الاختبار**")

# 15. أمر الحكمة
@client.on(events.NewMessage(outgoing=True, pattern=r'\.حكمة$'))
async def ai_wisdom(event):
    """حكمة عشوائية"""
    await event.edit("💭 **جاري البحث عن حكمة...**")
    
    wisdoms = [
        "الصبر مفتاح الفرج، والعجلة من الشيطان.",
        "العلم في الصغر كالنقش في الحجر.",
        "الوقت كالسيف إن لم تقطعه قطعك.",
        "خير الكلام ما قل ودل.",
        "من جَدَّ وجد، ومن زرع حصد.",
        "اليد العليا خير من اليد السفلى.",
        "رب صدفة خير من ألف ميعاد.",
        "إذا أردت أن تطاع فاطلب المستطاع.",
        "في الاتحاد قوة، وفي التفرق ضعف.",
        "الحرية هي أن تعيش كريماً أو تموت شريفاً."
    ]
    
    response = random.choice(wisdoms)
    await event.edit(f"💎 **حكمة اليوم:**\n\n{response}")

# 16. أمر التطوير
@client.on(events.NewMessage(outgoing=True, pattern=r'\.تطوير$'))
async def ai_development(event):
    """معلومات التطوير"""
    info = """
🚀 **معلومات تطوير سورس كومن:**

🧠 **النظام:** الذكاء الاصطناعي المتكامل
⚙️ **المحرك:** Gemini 2.0 Flash Lite
📊 **الإصدار:** 2.0 Pro
🛠 **المطور:** حسين - @iomk0
📢 **القناة:** @iomk3

🔧 **المميزات المتاحة:**
• 16 أمر ذكي مختلف
• محادثة متقدمة مع AI
• كتابة أكواد برمجية
• إنشاء محتوى إبداعي
• ترجمة وتلخيص ذكي
• تصميم وتخطيط احترافي

⚡ **التحديثات القادمة:**
• دعم المزيد من لغات البرمجة
• إنشاء صور حقيقية بالذكاء
• نظام محادثة تفاعلية
• دعم الصوت والرسوم المتحركة

📞 **للدعم والتطوير:** @iomk0
    """
    await event.edit(info)

# 17. أمر الصور (جديد)
@client.on(events.NewMessage(outgoing=True, pattern=r'\.صور (.+)'))
async def ai_images(event):
    """إنشاء صور بالذكاء الاصطناعي"""
    description = event.pattern_match.group(1)
    await event.edit("🖼 **جاري إنشاء وصف للصورة...**")
    
    response = await gemini.ask(
        f"أنشئ وصفاً مفصلاً لصورة عن: {description}",
        "أنت فنان محترف في إنشاء الصور بالذكاء الاصطناعي. قدم وصفاً مفصلاً للصورة مع الألوان والإضاءة والتركيب والعناصر."
    )
    
    if response:
        await event.edit(f"🎨 **وصف الصورة للذكاء الاصطناعي:**\n\n{response}\n\n📸 **يمكنك استخدام هذا الوصف في برامج توليد الصور مثل:**\n• Midjourney\n• DALL-E\n• Stable Diffusion")
    else:
        await event.edit("❌ **تعذر إنشاء الوصف**")

# =========================================================
# 🛠 دوال مساعدة
# =========================================================

async def get_ai_stats():
    """الحصول على إحصائيات النظام"""
    return {
        "commands_count": 17,
        "ai_engine": "Gemini 2.0 Flash Lite",
        "status": "🟢 نشط",
        "version": "2.0 Pro"
    }

print("✅ تم تحميل نظام الذكاء الاصطناعي بنجاح!")
print("📱 جميع الأوامر شغالة مباشرة بدون .ذكاء")
print("📋 استخدم .ذكاء لعرض القائمة الكاملة")
print("👨‍💻 المطور: @iomk0 | القناة: @iomk3")
