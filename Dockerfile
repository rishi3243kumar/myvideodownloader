FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install ffmpeg + deno (JS runtime for yt-dlp YouTube support)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl unzip && \
    curl -fsSL https://deno.land/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Add deno to PATH
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]
