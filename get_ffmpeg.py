import urllib.request
import zipfile
import io
import os
import shutil

url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
print("Downloading FFmpeg directly...")
response = urllib.request.urlopen(url)
print("Extracting...")
with zipfile.ZipFile(io.BytesIO(response.read())) as z:
    for file in z.namelist():
        if file.endswith("ffmpeg.exe"):
            z.extract(file, ".")
            # Move to current directory
            target = "ffmpeg.exe"
            if os.path.exists(target):
                os.remove(target)
            os.rename(file, target)
            break
print("Done! ffmpeg.exe is now in the bot folder.")
