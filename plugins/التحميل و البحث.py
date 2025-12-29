import os
import asyncio
import yt_dlp
import time
import certifi
from telethon import events
# الاستدعاء الصحيح لضمان عدم توقف الملف
from __main__ import client 

# --- التعديلة المطلوبة لظهور أمر واحد فقط في القائمة ---
SECTION_NAME = "🎬 قسم الميديا"
COMMANDS = "`.ميديا` - (أوامر التحميل والبحث الشامل)"
# -------------------------------------------------------

os.environ['SSL_CERT_FILE'] = certifi.where()

def get_pro_opts(is_audio=False, hook=None):
    """إعدادات محسنة لجميع المنصات بدون أخطاء"""
    opts = {
        'format': 'bestaudio/best' if is_audio else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title).100s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,  # تغيير لعرض معلومات التحليل
        'no_warnings': False,  # لعرض التحذيرات للتصحيح
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extract_flat': False,
        'force_generic_extractor': False,
        # إعدادات السرعة
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'continue_dl': True,
        'no_part': True,
        'hls_prefer_native': True,
        'external_downloader': 'aria2c',
        'external_downloader_args': ['--max-connection-per-server=16', '--min-split-size=1M', '--split=16'],
        # إعدادات لمعالجة TikTok والمشاكل الأخرى
        'extractor_retries': 3,
        'skip_unavailable_fragments': True,
        'keep_fragments': True,
        'trim_file_name': 200,
        # إعدادات التخزين
        'cachedir': 'downloads/cache',
        'no_color': True,
    }
    
    # إعدادات خاصة بالصوت
    if is_audio:
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'keepvideo': False,
            'prefer_ffmpeg': True,
            'writeinfojson': False,
            'writethumbnail': False,
        })
    
    # إعدادات extractor خاصة لـ TikTok والمنصات الأخرى
    opts.update({
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web']},
            'tiktok': {'app_version': '30.2.0', 'manifest_app_version': '2023103101'},
            'instagram': {'requested_clips_count': 1},
            'twitter': {'cards_platform': 'Web-12'},
        },
        # إضافة cookies شائعة للتجاوز
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
    })
    
    if hook:
        opts['progress_hooks'] = [hook]
    
    return opts

def progress_hook(d, event, loop, last_update_time):
    """شريط التقدم"""
    if d['status'] == 'downloading':
        current = time.time()
        if current - last_update_time[0] > 2:
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            
            if total and total > 0:
                percent = (downloaded * 100) / total
                bar_length = 10
                filled = int(bar_length * percent // 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                message = f"""
📥 **تحميل:** {bar} {percent:.1f}%
📊 **السرعة:** {speed}
⏱ **الوقت المتبقي:** {eta}
                """
                
                loop.create_task(event.edit(message.strip()))
                last_update_time[0] = current

async def universal_downloader(event, url, is_audio=False, is_search=False):
    """محمل شامل مع معالجة جميع الأخطاء"""
    await event.edit("🔍 **جاري التحليل والبحث...**")
    
    if not url or len(url.strip()) == 0:
        await event.edit("❌ **الرجاء إدخال رابط أو كلمة للبحث**")
        return
    
    last_update_time = [time.time()]
    loop = asyncio.get_event_loop()
    
    try:
        def download():
            # تحديد نوع البحث
            if is_search or not url.startswith(('http://', 'https://')):
                target = f"ytsearch1:{url}"
            else:
                target = url
            
            hook = lambda d: progress_hook(d, event, loop, last_update_time)
            opts = get_pro_opts(is_audio, hook)
            
            # إضافة إعدادات خاصة للمواقع المعقدة
            site_opts = {
                # تجاوز TikTok والمواقع المقيدة
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
                # محاولات متعددة لاستخراج المعلومات
                'extractor_retries': 5,
                'sleep_interval_requests': 1,
                'sleep_interval': 2,
                'max_sleep_interval': 5,
                # تحسين استخراج TikTok
                'overwrites': {
                    'tiktok:user': {
                        'endpoint': 'api/v1/item_list/',
                    }
                },
            }
            opts.update(site_opts)
            
            # محاولات مختلفة للمواقع المقيدة
            attempts = 0
            max_attempts = 3
            
            while attempts < max_attempts:
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        # معالجة TikTok بشكل خاص
                        if 'tiktok.com' in target.lower() and attempts > 0:
                            # تغيير الـ user-agent في المحاولات المتكررة
                            ydl.params['http_headers']['User-Agent'] = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{120 + attempts}.0.0.0 Safari/537.36'
                        
                        info = ydl.extract_info(target, download=True)
                        
                        if isinstance(info, dict) and 'entries' in info:
                            entries = [e for e in info['entries'] if e]
                            if entries:
                                info = entries[0]
                            else:
                                attempts += 1
                                continue
                        
                        # الحصول على المسار الصحيح
                        if is_audio:
                            # البحث عن ملف MP3 الذي تم إنشاؤه
                            base_name = os.path.splitext(ydl.prepare_filename(info))[0]
                            mp3_path = base_name + '.mp3'
                            
                            # إذا لم يتم إنشاء MP3، قم بإنشائه يدويًا
                            if not os.path.exists(mp3_path):
                                import subprocess
                                original_path = ydl.prepare_filename(info)
                                if os.path.exists(original_path):
                                    # تحويل إلى MP3 باستخدام FFmpeg
                                    cmd = ['ffmpeg', '-i', original_path, '-codec:a', 'libmp3lame', '-q:a', '2', mp3_path, '-y']
                                    subprocess.run(cmd, capture_output=True)
                                    if os.path.exists(original_path):
                                        os.remove(original_path)
                            path = mp3_path if os.path.exists(mp3_path) else ydl.prepare_filename(info)
                        else:
                            path = ydl.prepare_filename(info)
                        
                        return path, info
                        
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(2)  # انتظار قبل المحاولة التالية
            
            raise Exception(f"فشل بعد {max_attempts} محاولات")

        file_path, info = await asyncio.to_thread(download)
        
        # تنظيف العنوان
        title = info.get('title', 'ملف')
        if len(title) > 50:
            title = title[:47] + "..."
        
        await event.edit("📤 **جاري الرفع فائق السرعة...**")
        
        # رفع الملف
        try:
            if is_audio:
                # رفع كملف صوتي قابل للتشغيل والحفظ
                result = await client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"🎵 **{title}**\n\n💾 **يمكنك حفظه وحفظه في التطبيقات**\n🎧 قابلة للتشغيل المباشر\n💎 **SOURCE COMMON**",
                    voice_note=True,  # قابلة للتشغيل كملف صوتي
                    force_document=False,  # ليس كملف وثيقة عادي
                    allow_cache=False,
                    part_size_kb=512,
                    # إعدادات تسمح بالحفظ
                    attributes=[
                        types.DocumentAttributeAudio(
                            duration=info.get('duration', 0),
                            voice=True,
                            title=title,
                            performer=info.get('uploader', 'SOURCE COMMON'),
                        )
                    ] if not is_search else None,
                )
            else:
                # رفع كفيديو
                result = await client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"🎬 **{title}**\n\n📹 يدعم التشغيل المباشر والحفظ\n💎 **SOURCE COMMON**",
                    supports_streaming=True,
                    force_document=False,
                    allow_cache=False,
                    part_size_kb=1024,
                )
            
            # حذف رسالة التحميل
            await event.delete()
            
        except Exception as send_error:
            # محاولة بديلة
            try:
                from telethon import types
                await client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"✅ **{title}**\n💎 **SOURCE COMMON**",
                    force_document=True,  # كوثيقة عادية للتأكد من العمل
                )
                await event.delete()
            except:
                await event.edit(f"❌ **خطأ في الرفع:** {str(send_error)[:80]}")
        
        # تنظيف الملفات
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            # تنظيف المجلد
            for root, dirs, files in os.walk('downloads', topdown=False):
                for name in files:
                    if name.endswith(('.part', '.ytdl', '.tmp', '.temp')):
                        try:
                            os.remove(os.path.join(root, name))
                        except:
                            pass
        except:
            pass
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        # معالجة أخطاء TikTok
        if 'tiktok' in error_msg.lower() or 'unable to extract' in error_msg.lower():
            # محاولة استخدام طريقة بديلة لـ TikTok
            try:
                await event.edit("🔄 **جرب مع TikTok بطريقة مختلفة...**")
                # استخدام نسخة بديلة من TikTok extractor
                def tiktok_fix():
                    import subprocess
                    import json
                    
                    # محاولة استخدام طريقة بديلة
                    temp_url = url if not is_search else f"ytsearch:{url}"
                    cmd = ['yt-dlp', '-j', '--no-warnings', temp_url]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        info = json.loads(result.stdout)
                        if isinstance(info, list):
                            info = info[0]
                        
                        # تنزيل الملف
                        if is_audio:
                            cmd_dl = ['yt-dlp', '-x', '--audio-format', 'mp3', '--output', 'downloads/%(title)s.%(ext)s', info['webpage_url']]
                        else:
                            cmd_dl = ['yt-dlp', '-f', 'best', '--output', 'downloads/%(title)s.%(ext)s', info['webpage_url']]
                        
                        subprocess.run(cmd_dl, capture_output=True)
                        
                        # العثور على الملف المنزل
                        import glob
                        pattern = 'downloads/*'
                        files = glob.glob(pattern)
                        if files:
                            return max(files, key=os.path.getctime), info
                    
                    raise Exception("فشل تحميل TikTok")
                
                file_path, info = await asyncio.to_thread(tiktok_fix)
                
                # متابعة الرفع
                title = info.get('title', 'ملف TikTok')
                await client.send_file(event.chat_id, file_path, caption=f"✅ **{title}**\n💎 **SOURCE COMMON**")
                await event.delete()
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                return
                
            except Exception as fix_error:
                await event.edit(f"❌ **خطأ في TikTok:** حاول استخدام الرابط من متصفح آخر")
        
        elif "No video results" in error_msg or "Unable to download webpage" in error_msg:
            await event.edit("❌ **لم يتم العثور على نتائج. تأكد من الرابط أو جرب كلمات أخرى**")
        elif "Video unavailable" in error_msg:
            await event.edit("❌ **الفيديو غير متاح أو محذوف**")
        elif "Private" in error_msg or "Sign in" in error_msg:
            await event.edit("❌ **المحتوى خاص أو يتطلب تسجيل دخول**")
        else:
            await event.edit(f"❌ **خطأ:** `{error_msg[:100]}`")
    
    except Exception as e:
        error_msg = str(e)
        await event.edit(f"❌ **خطأ غير متوقع:** `{error_msg[:100]}`")

# استيراد types في حالة عدم وجوده
try:
    from telethon import types
except:
    pass

# الأوامر كما هي
@client.on(events.NewMessage(outgoing=True, pattern=r'\.فيديو (.*)'))
async def video_cmd(event):
    await universal_downloader(event, event.pattern_match.group(1).strip(), False, False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.صوت (.*)'))
async def audio_cmd(event):
    await universal_downloader(event, event.pattern_match.group(1).strip(), True, False)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_فيد (.*)'))
async def search_video_cmd(event):
    await universal_downloader(event, event.pattern_match.group(1).strip(), False, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.بحث_صوت (.*)'))
async def search_audio_cmd(event):
    await universal_downloader(event, event.pattern_match.group(1).strip(), True, True)

@client.on(events.NewMessage(outgoing=True, pattern=r'\.ميديا'))
async def media_help(event):
    """عرض قائمة الأوامر"""
    help_text = """
🎬 **أوامر الميديا - النسخة المحسنة**

📥 **تحميل مباشر:**
▫️ `.فيديو` + رابط
▫️ `.صوت` + رابط

🔍 **بحث شامل:**
▫️ `.بحث_فيد` + كلمات
▫️ `.بحث_صوت` + كلمات

✅ **مميزات محسنة:**
▫️ يدعم TikTok وجميع المنصات
▫️ صوت قابل للحفظ والتشغيل
▫️ سرعة فائقة في الرفع
▫️ معالجة جميع الأخطاء

💡 **الملاحظات:**
▫️ الصوتيات قابلة للحفظ في التطبيقات
▫️ يدعم معظم مواقع الفيديو
▫️ الرفع تلقائي وسريع
    """
    await event.edit(help_text.strip())
