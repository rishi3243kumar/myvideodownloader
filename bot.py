import os
import asyncio
import logging
import uuid
import re
from functools import partial
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot version - v1.1

# Environment Variables for Configuration
# Debug: print all env vars to diagnose Railway injection
logger.info(f"All env keys: {list(os.environ.keys())}")
logger.info(f"API_ID present: {'API_ID' in os.environ}")
logger.info(f"API_HASH present: {'API_HASH' in os.environ}")
logger.info(f"BOT_TOKEN present: {'BOT_TOKEN' in os.environ}")

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error(f"Missing vars! API_ID={API_ID}, API_HASH={'set' if API_HASH else None}, BOT_TOKEN={'set' if BOT_TOKEN else None}")
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

# Initialize Pyrogram Client
app = Client(
    "video_downloader_bot",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Regex to detect URLs
URL_REGEX = re.compile(r'https?://[^\s]+')

# Store URLs temporarily. Key: message_id, Value: URL string
user_requests = {}

@app.on_message(filters.command(["start", "help"]))
async def start_handler(client: Client, message: Message):
    welcome_text = (
        "👋 **Welcome to the Cloud Video Downloader Bot!**\n\n"
        "Send me any supported video link (YouTube, Instagram, X/Twitter, etc.) "
        "and I will download and send it directly to you.\n\n"
        "**Features:**\n"
        "🚀 Fast MTProto downloads\n"
        "☁️ 100% Cloud-native execution\n"
        "🎥 Choose your Quality & Format\n"
        "💾 Zero Storage Accumulation\n\n"
        "Just send a link to get started!"
    )
    await message.reply_text(welcome_text)

def download_video_sync(url: str, output_template: str, quality: str) -> dict:
    """
    Blocking function to download video using yt-dlp.
    """
    
    format_selector = 'best'
    if quality == '1080p':
        format_selector = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best'
    elif quality == '720p':
        format_selector = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best'
    elif quality == '480p':
        format_selector = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best'
    elif quality == 'audio':
        format_selector = 'bestaudio[ext=m4a]/bestaudio/best'

    # On Linux (cloud), ffmpeg is in PATH. On Windows (local), use local exe.
    ffmpeg_path = os.path.abspath('ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe') if os.path.exists('ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe') else 'ffmpeg'
    ydl_opts = {
        'format': format_selector,
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ffmpeg_location': ffmpeg_path,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
            }
        }, # Permanent Bypass for YouTube bot checks without cookies
        'max_filesize': 500 * 1024 * 1024, # 500MB max limit
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def handle_url(client: Client, message: Message):
    url_match = URL_REGEX.search(message.text)
    if not url_match:
        await message.reply_text("Please send a valid URL.")
        return

    url = url_match.group(0)
    
    # Store URL in memory
    user_requests[message.id] = url
    
    # Send Inline Keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎥 1080p", callback_data=f"dl_1080p_{message.id}"),
            InlineKeyboardButton("🎥 720p", callback_data=f"dl_720p_{message.id}")
        ],
        [
            InlineKeyboardButton("🎥 480p", callback_data=f"dl_480p_{message.id}"),
            InlineKeyboardButton("🎵 Audio", callback_data=f"dl_audio_{message.id}")
        ]
    ])
    
    await message.reply_text("Select format & quality to download:", reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^dl_"))
async def callback_handler(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    quality = data[1]
    message_id = int(data[2])
    
    url = user_requests.get(message_id)
    
    if not url:
        await callback_query.answer("Link expired or not found. Please send the link again.", show_alert=True)
        return
        
    await callback_query.answer("Starting download...")
    
    # Remove the buttons and show status
    status_msg = await callback_query.message.edit_text(f"⏳ Downloading on cloud ({quality})...")
    
    # Generate unique filename for concurrent processing
    file_id = str(uuid.uuid4())
    temp_dir = "/tmp" if os.path.exists("/tmp") else "."
    
    # For audio, use m4a extension if possible, else rely on yt-dlp default
    output_template = os.path.join(temp_dir, f"{file_id}.%(ext)s")
    
    downloaded_file = None
    
    try:
        loop = asyncio.get_event_loop()
        # Run blocking yt-dlp in executor
        download_task = partial(download_video_sync, url, output_template, quality)
        downloaded_file, info = await loop.run_in_executor(None, download_task)
        
        if not downloaded_file or not os.path.exists(downloaded_file):
            raise Exception("Failed to download file.")
            
        file_size = os.path.getsize(downloaded_file)
        if file_size > 500 * 1024 * 1024: # 500 MB limit for Telegram bots
            raise Exception("File is larger than Telegram's 500MB limit for bots.")
            
        await status_msg.edit_text("📤 Uploading to Telegram...")
        
        title = info.get('title', 'Media')
        duration = info.get('duration', 0)
        
        # Upload using Pyrogram
        if quality == 'audio':
            await client.send_audio(
                chat_id=callback_query.message.chat.id,
                audio=downloaded_file,
                caption=f"**{title}**\n\nDownloaded via Bot",
                duration=duration
            )
        else:
            width = info.get('width', 0)
            height = info.get('height', 0)
            await client.send_video(
                chat_id=callback_query.message.chat.id,
                video=downloaded_file,
                caption=f"**{title}**\n\nDownloaded via Bot ({quality})",
                supports_streaming=True,
                duration=duration,
                width=width,
                height=height
            )
        
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")
        
    finally:
        # ZERO Storage Accumulation: Always clean up
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
                logger.info(f"Cleaned up file: {downloaded_file}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up {downloaded_file}: {cleanup_error}")
        
        # Cleanup memory
        if message_id in user_requests:
            del user_requests[message_id]

if __name__ == "__main__":
    logger.info("Starting bot...")
    app.run()
