import os
import time
import re
import subprocess
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
CHANNELS = {
    "TateSpeech": "https://rumble.com/c/TateSpeech",
    "TateConfidential": "https://rumble.com/c/tateconfidential"
}
RAW_DIR = "/Users/uttakarsh/Desktop/Tate/data/raw"
os.makedirs(RAW_DIR, exist_ok=True)
MAX_VIDEOS = 90

def sanitize_filename(text, length=30):
    text = re.sub(r"[\\/:*?\"<>|]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:length].strip("_")

def get_video_links(channel_url, max_videos=100):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(channel_url)
    time.sleep(5)

    links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    while len(links) < max_videos and scroll_attempts < 20:
        video_elems = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/v"]')
        for elem in video_elems:
            href = elem.get_attribute('href')
            if href and href.startswith("https://rumble.com/v") and '/v' in href:
                links.add(href)
            if len(links) >= max_videos:
                break

        print(f"Scrolling... current link count: {len(links)}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            last_height = new_height

    driver.quit()
    return list(links)[:max_videos]


    driver.quit()
    return list(links)[:max_videos]

def download_video(url, out_dir):
    try:
        result = subprocess.run(
            ["yt-dlp", "--extract-audio", "--audio-format", "mp3", "-o", f"{out_dir}/%(id)s.%(ext)s", url],
            capture_output=True, text=True, check=True
        )
        match = re.search(r"\[ExtractAudio\] Destination: (.+)", result.stdout)
        if match:
            return match.group(1).strip()
        for file in os.listdir(out_dir):
            if file.endswith(".mp3"):
                return os.path.join(out_dir, file)
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e}")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
    return None

def transcribe_audio(audio_path):
    try:
        import whisper
    except ImportError:
        print("Whisper not installed. Run: pip install openai-whisper")
        return None

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Transcription failed: {e}")
        return None

def process_channel(channel_name, channel_url):
    print(f"\nProcessing channel: {channel_name}")
    links = get_video_links(channel_url, MAX_VIDEOS)
    print(f"Found {len(links)} video links")
    saved = 0

    for idx, url in enumerate(links, 1):
        video_id = url.split('/')[-1].split('-')[0]
        out_txt = os.path.join(RAW_DIR, f"{channel_name}_{video_id}.txt")
        if os.path.exists(out_txt):
            print(f"Already exists: {out_txt}")
            continue

        print(f"({idx}/{MAX_VIDEOS}) Downloading: {url}")
        clean_url = url.split('?')[0]
        audio_path = download_video(clean_url, RAW_DIR)
        if not audio_path:
            print("Skipping due to download error.")
            continue

        print("Transcribing...")
        transcript = transcribe_audio(audio_path)
        if transcript and transcript.strip():
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"Saved transcript: {out_txt}")
            saved += 1
        else:
            print("No transcript saved (empty or failed).")

        try:
            os.remove(audio_path)
        except Exception:
            pass

        if saved >= MAX_VIDEOS:
            break

    print(f"Total transcripts saved for {channel_name}: {saved}")

if __name__ == "__main__":
    if not shutil.which("ffmpeg"):
        raise EnvironmentError("ffmpeg not found. Please install it with 'brew install ffmpeg'")
    for name, url in CHANNELS.items():
        process_channel(name, url)
