import os
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from youtubesearchpython import VideosSearch

RAW_DIR = "/Users/uttakarsh/Desktop/Tate/data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

SEARCH_TERMS = [
    "Andrew Tate", "Tate", "Cobra Tate", "Tate speech",
    "Tate podcast", "Tate interview", "Tate motivation"
]
PAGES_PER_TERM = 10  # 10 pages × 50 = 500 videos per term (with deduplication)
VIDEOS_PER_PAGE = 50
SLEEP_BETWEEN_TRANSCRIPTS = 0.5
TARGET_TRANSCRIPTS = 200

def get_video_ids():
    all_ids = set()
    for term in SEARCH_TERMS:
        print(f"Searching for: {term}")
        search = VideosSearch(term, limit=VIDEOS_PER_PAGE)
        for _ in range(PAGES_PER_TERM):
            results = search.result().get("result", [])
            for video in results:
                if video.get("type") == "video":
                    all_ids.add(video["id"])
            try:
                search.next()
            except Exception:
                break  # No more pages
            time.sleep(1)
    print(f"Found {len(all_ids)} unique video IDs.")
    return list(all_ids)

def save_transcript(video_id, transcript):
    out_path = os.path.join(RAW_DIR, f"{video_id}.txt")
    if os.path.exists(out_path):
        print(f"Already exists: {video_id}")
        return False
    try:
        text = " ".join([entry["text"] for entry in transcript])
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved transcript for {video_id}")
        return True
    except Exception as e:
        print(f"Error saving {video_id}: {e}")
        return False

def scrape_and_save_all():
    video_ids = get_video_ids()
    saved_count = 0
    idx = 0
    while saved_count < TARGET_TRANSCRIPTS and idx < len(video_ids):
        vid = video_ids[idx]
        try:
            print(f"({saved_count+1}/{TARGET_TRANSCRIPTS}) Fetching transcript for: {vid}")
            # Try for English transcript first
            try:
                transcript = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
            except NoTranscriptFound:
                # Fallback to any available transcript (including auto-generated)
                transcript = YouTubeTranscriptApi.get_transcript(vid)
            if save_transcript(vid, transcript):
                saved_count += 1
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
            print(f"Skipped {vid}: {str(e)}")
        except Exception as e:
            print(f"Failed {vid}: {str(e)}")
        idx += 1
        time.sleep(SLEEP_BETWEEN_TRANSCRIPTS)
    print(f"Finished. {saved_count} transcripts saved to {RAW_DIR}")

if __name__ == "__main__":
    scrape_and_save_all()
