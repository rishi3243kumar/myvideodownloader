# Telegram Video Downloader Bot

A production-ready, cloud-native Telegram Video Downloader Bot built in Python using Pyrogram (MTProto) and yt-dlp.

## Features
- **High Speed:** Uses Pyrogram v2 with TgCrypto for MTProto native high-speed transfers.
- **Universal Media Extraction:** Powered by `yt-dlp` to download from YouTube, Instagram, X/Twitter, Facebook, Google Drive, and more.
- **100% Cloud-Native:** Designed to run on remote servers (Render, Koyeb, VPS) with zero local storage footprint.
- **Strict Memory Management:** Instant auto-cleanup of files using `try-finally` blocks.
- **Asynchronous Processing:** Concurrent multi-user downloads without blocking the event loop.

## Prerequisites
- A Telegram account to get API keys.
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).
- A free account on Render, Koyeb, or an Ubuntu VPS.

## Environment Variables
The bot requires the following environment variables to run:
- `API_ID`: Get this from [my.telegram.org](https://my.telegram.org)
- `API_HASH`: Get this from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN`: Get this from [@BotFather](https://t.me/BotFather)

## Deployment Guides

### Option 1: Deploy to Koyeb / Render (Free Cloud Providers)

1. **Fork or Push to GitHub**: Push this repository to your own GitHub account.
2. **Create a Service**:
   - On **Koyeb**: Click "Create App", select GitHub, choose your repository.
   - On **Render**: Click "New", select "Web Service" or "Background Worker", connect your GitHub, choose your repository.
3. **Configure Environment Variables**:
   - In the service settings, add `API_ID`, `API_HASH`, and `BOT_TOKEN` as environment variables.
4. **Deploy**:
   - Both platforms will automatically detect the `Dockerfile` and start building your image.
   - Once the build succeeds, the bot will start automatically.

### Option 2: Deploy to an Ubuntu VPS using Docker

If you have your own Ubuntu VPS (e.g., from DigitalOcean, Hetzner, AWS), follow these steps:

1. **Install Docker**:
   ```bash
   sudo apt update
   sudo apt install docker.io -y
   ```

2. **Clone the Repository**:
   ```bash
   git clone <your-github-repo-url>
   cd <your-repo-name>
   ```

3. **Build the Docker Image**:
   ```bash
   sudo docker build -t telegram-video-bot .
   ```

4. **Run the Container**:
   Replace the placeholders with your actual keys. We use `-d` to run it in the background.
   ```bash
   sudo docker run -d \
     --name video_bot \
     -e API_ID="your_api_id" \
     -e API_HASH="your_api_hash" \
     -e BOT_TOKEN="your_bot_token" \
     telegram-video-bot
   ```

5. **Check Logs**:
   ```bash
   sudo docker logs -f video_bot
   ```

## Local Development (Optional)
If you want to test the bot locally:
1. Ensure you have Python 3.11+ and `ffmpeg` installed on your system.
2. Install requirements: `pip install -r requirements.txt`
3. Set environment variables in your terminal:
   - Windows (PowerShell): `$env:API_ID="12345"; $env:API_HASH="abc"; $env:BOT_TOKEN="token"`
   - Linux/Mac: `export API_ID="12345" API_HASH="abc" BOT_TOKEN="token"`
4. Run: `python bot.py`
