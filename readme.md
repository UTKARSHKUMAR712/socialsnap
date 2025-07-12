# SocialSnap 🚀

**Download videos from any social media platform with ease!** SocialSnap is a cutting-edge, user-friendly tool that lets you grab videos from YouTube, Instagram, TikTok, Facebook, and over 600+ other platforms in a snap. With a sleek interface, fast downloads, and no registration required, it’s your go-to solution for capturing content.

- **Creator**: Utkarsh Kumar
- **Version**: 2.0.0
- **Last Updated**: 12:05 PM IST, Friday, July 11, 2025
- **Website**: [Coming Soon] | [GitHub](https://github.com/your-username/socialsnap)
<img width="1919" height="1078" alt="Screenshot 2025-07-12 123840" src="https://github.com/user-attachments/assets/64c9cce8-3fe4-417a-805f-9c28026f22b0" />
<img width="1919" height="1079" alt="Screenshot 2025-07-12 123853" src="https://github.com/user-attachments/assets/ec6e9850-ae3b-41bb-84d0-9a8d4133e181" />

---
## ✨ What’s New
Real-time download progress bar
Now shows live percentage updates during downloading, giving instant feedback.

Detailed status & merging info
Displays the current file name, merging status, and clear completion messages directly in the UI.

ETA & Speed display ready
Backend hooked with yt-dlp hooks; front-end is structured to show ETA and speed (expandable in future updates).

Playlist support improved
Each video in a playlist is now downloaded in order, with per-item progress and status.

Smart merging with FFmpeg
Automatically merges separate video+audio streams into a single MP4 file using FFmpeg, with error handling and cleanup.

Safe, clean file naming
Automatically sanitizes filenames to avoid filesystem errors.

Custom Downloads directory
Media is saved under ~/Downloads/SocialSnap on all systems for easy access.

## 🐛 Fixes & Stability
Fixed critical Rectangle.op_Equality crash by properly isolating the webview.js_api object.

Fixed lambda() threading bug that caused TypeError on window binding.

Enhanced error reporting for unavailable formats and FFmpeg failures.

## ⚙ Tech Stack
Python 3.12

yt-dlp for downloading

FFmpeg for merging

pywebview for cross-platform GUI

Custom HTML/JS front-end with dynamic JS bridge

## ✨ Features

- **Cross-Platform Support**: Download from 600+ platforms including YouTube, Instagram, TikTok, Twitter, and more.
- **High-Quality Options**: Choose from MP4, MP3, HD, 4K, and other formats.
- **Blazing Fast**: High-speed downloads with No wait time.
- **Secure & Private**: 100% safe with no malware or data tracking.
- **Interactive UI**: Modern design with animated icons, smooth scrolling, and a dynamic modal for platform lists.
- **Easy Navigation**: Scroll to key sections with the "Start Now" button.

---

## 🎥 Demo

Check out SocialSnap in action! (Add a GIF or video link here once available, e.g., `[Demo GIF](https://github.com/your-username/socialsnap/raw/main/demo.gif)`)

---

## 🚀 Getting Started

### Prerequisites

- Stable internet connection.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/UTKARSHKUMAR712/socialsnap.git
2.Run it:

    python python main.py  
   
