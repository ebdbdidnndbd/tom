# main_core.py - المحرك العالمي الجديد لسورس كومن
import os, sys, asyncio, importlib
from telethon import TelegramClient
from telethon.sessions import StringSession

# إعدادات ثابتة للمنظومة
API_ID = 22439859
API_HASH = '312858aa733a7bfacf54eede0c275db4'

class CommonEngine:
    def __init__(self, session_str, user_id):
        self.client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        self.user_id = user_id
        self.plugins = {}

    async def load_plugins(self):
        """محرك جلب الإضافات التلقائي لضمان الاحترافية"""
        if not os.path.exists("plugins"):
            os.makedirs("plugins")
        
        # كود لجلب كل ميزة من ملفها الخاص لسرعة الأداء
        for file in os.listdir("plugins"):
            if file.endswith(".py"):
                name = file[:-3]
                module = importlib.import_module(f"plugins.{name}")
                if hasattr(module, "setup"):
                    await module.setup(self.client)
                self.plugins[name] = module

    async def run(self):
        await self.client.connect()
        if await self.client.is_user_authorized():
            print(f"🚀 سورس كومن انطلق للحساب: {self.user_id}")
            await self.load_plugins()
            await self.client.run_until_disconnected()

# نظام الحماية من التوقف المفاجئ
if __name__ == "__main__":
    # تشغيل المنظومة
    pass
