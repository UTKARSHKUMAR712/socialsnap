import os
import json
import subprocess
import webview
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

# Download folder
HOME_DIR = os.path.expanduser("~")
DOWNLOAD_DIR = os.path.join(HOME_DIR, "Downloads", "SocialSnap")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def clean_title(title):
    return "".join(c for c in title if c.isalnum() or c in " _-.").strip(" _-.")

class ApiBridge:
    def __init__(self):
        self._info_cache = {}

    def get_formats(self, url):
        try:
            with YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            if info.get('_type') == 'playlist' and 'entries' in info and info['entries']:
                info = info['entries'][0]

            self._info_cache[url] = info

            formats = []
            for f in info.get("formats", []):
                if not f.get("format_id"):
                    continue
                acodec, vcodec, ext = f.get("acodec", "none"), f.get("vcodec", "none"), f.get("ext", "N/A")
                label, typ = "", ""
                if acodec != "none" and vcodec == "none":
                    abr = f.get("abr")
                    label = f"🎧 Audio | {round(abr)} kbps ({ext})" if abr else f"🎧 Audio | ({ext})"
                    typ = "audio"
                elif vcodec != "none" and acodec == "none":
                    h = f.get("height")
                    label = f"🎬 Video | {h}p ({ext})" if h else f"🎬 Video | ({ext})"
                    typ = "video"
                elif acodec != "none" and vcodec != "none":
                    h = f.get("height")
                    label = f"📦 Combined | {h}p ({ext})" if h else f"📦 Combined | ({ext})"
                    typ = "combined"
                else:
                    continue

                formats.append({"id": f["format_id"], "label": label, "type": typ, "ext": ext})

            formats.sort(key=lambda x: ("combined", "video", "audio").index(x["type"]))
            return json.dumps({
                "status": "success",
                "title": info.get("title", "Unknown Title"),
                "thumbnail": info.get("thumbnail"),
                "formats": formats
            })
        except DownloadError:
            return json.dumps({"status": "error", "message": "Failed to fetch format information. Please check the link."})
        except Exception as e:
            return json.dumps({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})

    def download(self, url, format_id):
        try:
            with YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            # Playlist
            if info.get('_type') == 'playlist':
                for idx, entry in enumerate(info.get('entries', []), start=1):
                    video_url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry['id']}"
                    title = entry.get("title", f"Video {idx}")
                    window.evaluate_js(f"updateCurrentName('📥 Downloading: {title}'); updateProgressBar(0);")
                    result = json.loads(self.download(video_url, format_id))
                    if result.get("status") != "success":
                        return json.dumps({
                            "status": "error",
                            "message": f"Failed on video {idx}: {result.get('message')}"
                        })
                return json.dumps({"status": "success", "message": "All playlist videos downloaded successfully."})

            # Single video
            title = info.get("title", "media_file")
            safe_title = clean_title(title)
            window.evaluate_js(f"updateCurrentName('📥 Downloading: {title}'); updateProgressBar(0);")

            selected = next((f for f in info["formats"] if f["format_id"] == format_id), None)
            if not selected:
                return json.dumps({"status": "error", "message": "Selected format not found."})

            acodec, vcodec, ext = selected.get("acodec", "none"), selected.get("vcodec", "none"), selected.get("ext")

            def progress_hook(d):
                if d['status'] == 'downloading':
                    pct = d.get('_percent_str', '0%').replace('%', '').strip()
                    try:
                        pct = int(float(pct))
                        window.evaluate_js(f"updateProgressBar({pct});")
                    except:
                        pass

            if acodec != 'none' and vcodec == 'none':
                out_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.{ext}")
                with YoutubeDL({"format": format_id, "outtmpl": out_path, "quiet": True, "progress_hooks": [progress_hook]}) as ydl:
                    ydl.download([url])
                window.evaluate_js(f"updateProgressBar(100); updateCurrentName('✅ Downloaded audio: {title}');")
                return json.dumps({"status": "success", "message": f"Downloaded audio: {title}"})

            elif acodec != 'none' and vcodec != 'none':
                out_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")
                with YoutubeDL({"format": format_id, "outtmpl": out_path, "merge_output_format": "mp4", "quiet": True, "progress_hooks": [progress_hook]}) as ydl:
                    ydl.download([url])
                window.evaluate_js(f"updateProgressBar(100); updateCurrentName('✅ Downloaded video: {title}');")
                return json.dumps({"status": "success", "message": f"Downloaded video: {title}"})

            elif vcodec != 'none' and acodec == 'none':
                audio_streams = [f for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
                if not audio_streams:
                    return json.dumps({"status": "error", "message": "No audio-only formats available to merge."})

                best_audio = sorted(audio_streams, key=lambda f: f.get("abr") or 0, reverse=True)[0]

                video_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}_video.{ext}")
                audio_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}_audio.{best_audio['ext']}")
                final_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

                with YoutubeDL({"format": format_id, "outtmpl": video_path, "quiet": True, "progress_hooks": [progress_hook]}) as ydl:
                    ydl.download([url])
                with YoutubeDL({"format": best_audio["format_id"], "outtmpl": audio_path, "quiet": True, "progress_hooks": [progress_hook]}) as ydl:
                    ydl.download([url])

                if not os.path.exists(video_path) or not os.path.exists(audio_path):
                    for f in (video_path, audio_path):
                        try: os.remove(f)
                        except: pass
                    return json.dumps({"status": "error", "message": "Streams failed to download."})

                window.evaluate_js(f"updateCurrentName('🔄 Merging audio + video for {title}...');")
                cmd = ["ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c", "copy", final_path]
                result = subprocess.run(cmd, capture_output=True, text=True)

                for f in (video_path, audio_path):
                    try: os.remove(f)
                    except: pass

                if result.returncode != 0 or not os.path.exists(final_path):
                    return json.dumps({"status": "error", "message": f"FFmpeg failed:\n{result.stderr}"})

                window.evaluate_js(f"updateProgressBar(100); updateCurrentName('✅ Successfully merged: {title}');")
                return json.dumps({"status": "success", "message": f"Merged: {title}"})

        except FileNotFoundError:
            return json.dumps({"status": "error", "message": "FFmpeg not found. Please ensure it's in your system PATH."})
        except Exception as e:
            msg = str(e)
            if "Requested format is not available" in msg:
                return json.dumps({"status": "error", "message": "⚠️ Please choose a different format."})
            return json.dumps({"status": "error", "message": f"Unexpected error: {msg}"})


if __name__ == "__main__":
    api = ApiBridge()
    window = webview.create_window("SocialSnap Media Downloader", "web/index.html", js_api=api, width=1200, height=800)
    webview.start()
