import os
import json
import subprocess
import webview
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

# Download folder setup (platform-safe)
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
            self._info_cache[url] = info

            formats = []
            for f in info.get("formats", []):
                if not f.get("format_id"):
                    continue
                acodec = f.get("acodec", "none")
                vcodec = f.get("vcodec", "none")
                ext = f.get("ext", "N/A")

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
            info = self._info_cache.get(url)
            if not info:
                with YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)

            title = info.get("title", "media_file")
            safe_title = clean_title(title)

            selected = next((f for f in info["formats"] if f["format_id"] == format_id), None)
            if not selected:
                return json.dumps({"status": "error", "message": "Selected format not found."})

            acodec = selected.get("acodec", "none")
            vcodec = selected.get("vcodec", "none")
            ext = selected.get("ext")

            if acodec != 'none' and vcodec == 'none':
                out_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.{ext}")
                with YoutubeDL({"format": format_id, "outtmpl": out_path, "quiet": True}) as ydl:
                    ydl.download([url])
                return json.dumps({"status": "success", "message": f"Downloaded audio: {title}"})

            elif acodec != 'none' and vcodec != 'none':
                out_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")
                with YoutubeDL({"format": format_id, "outtmpl": out_path, "merge_output_format": "mp4", "quiet": True}) as ydl:
                    ydl.download([url])
                return json.dumps({"status": "success", "message": f"Downloaded video: {title}"})

            elif vcodec != 'none' and acodec == 'none':
                audio_streams = [f for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
                if not audio_streams:
                    return json.dumps({"status": "error", "message": "No audio-only formats available to merge."})

                best_audio = sorted(audio_streams, key=lambda f: f.get("abr") or 0, reverse=True)[0]

                video_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}_video.{ext}")
                audio_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}_audio.{best_audio['ext']}")
                final_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

                with YoutubeDL({"format": format_id, "outtmpl": video_path, "quiet": True}) as ydl:
                    ydl.download([url])

                with YoutubeDL({"format": best_audio["format_id"], "outtmpl": audio_path, "quiet": True}) as ydl:
                    ydl.download([url])

                if not os.path.exists(video_path) or not os.path.exists(audio_path):
                    for f in (video_path, audio_path):
                        try: os.remove(f)
                        except: pass
                    return json.dumps({"status": "error", "message": "One of the streams failed to download."})

                cmd = ["ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c", "copy", final_path]
                result = subprocess.run(cmd, capture_output=True, text=True)

                for f in (video_path, audio_path):
                    try: os.remove(f)
                    except: pass

                if result.returncode != 0 or not os.path.exists(final_path):
                    return json.dumps({"status": "error", "message": f"FFmpeg failed:\n{result.stderr}"})

                return json.dumps({"status": "success", "message": f"Successfully merged: {title}"})

        except FileNotFoundError:
            return json.dumps({"status": "error", "message": "FFmpeg not found. Please ensure it's in your system PATH."})
        except Exception as e:
            msg = str(e)
            if "Requested format is not available" in msg:
                return json.dumps({
                    "status": "error",
                    "message": "⚠️ Please choose a different format — the one you selected is not currently available."
                })
            return json.dumps({"status": "error", "message": f"An unexpected error occurred: {msg}"})

if __name__ == "__main__":
    api = ApiBridge()
    webview.create_window("SocialSnap Media Downloader", "web/index.html", js_api=api, width=1200, height=800)
    webview.start()
