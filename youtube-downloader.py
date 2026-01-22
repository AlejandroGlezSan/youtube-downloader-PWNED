#!/usr/bin/env python3
"""
YouTube to MP3 Downloader - Fixed File Location Version
"""

import os
import sys
import yt_dlp
from pathlib import Path
import platform

def get_default_download_path():
    """Get system-specific default download path"""
    system = platform.system()
    
    if system == "Windows":
        # Windows default downloads folder
        downloads = Path.home() / "Downloads"
    elif system == "Darwin":  # macOS
        downloads = Path.home() / "Downloads"
    else:  # Linux and others
        downloads = Path.home() / "Downloads"
    
    # Create a subdirectory for our downloads
    youtube_downloads = downloads / "YouTube_MP3"
    youtube_downloads.mkdir(exist_ok=True)
    return str(youtube_downloads)

def find_downloaded_file(video_title, search_path=None):
    """Search for the downloaded file"""
    if search_path is None:
        search_path = os.getcwd()  # Current directory
    
    print(f"\n🔍 Searching for downloaded file...")
    print(f"📂 Search location: {search_path}")
    
    # Look for files with similar names
    video_title_clean = video_title.replace("/", "_").replace("\\", "_").replace(":", "_")
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.lower().endswith('.mp3') and video_title_clean in file:
                full_path = os.path.join(root, file)
                print(f"✅ Found: {full_path}")
                print(f"📏 Size: {os.path.getsize(full_path) / (1024*1024):.2f} MB")
                return full_path
    
    print("❌ Could not find the MP3 file automatically.")
    return None

def download_youtube_as_mp3(url, output_path=None, quality="192"):
    """
    Download a YouTube video as MP3 file with better error handling
    """
    if output_path is None:
        output_path = get_default_download_path()
    
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Get video title first
    try:
        print(f"🔗 Processing URL: {url}")
        print(f"📁 Will save to: {output_path}")
        
        # First get info without downloading
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown_Title')
            print(f"🎵 Video title: {video_title}")
            
            # Clean title for filename
            safe_title = ydl.prepare_filename(info)
            safe_title = os.path.splitext(safe_title)[0]
            
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return None
    
    # Configure download options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        # Less verbose output
        'verbose': False,
    }
    
    try:
        print(f"⬇️  Downloading audio at {quality}kbps...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Expected filename
        expected_filename = os.path.join(output_path, f"{safe_title}.mp3")
        
        if os.path.exists(expected_filename):
            print(f"\n✅ Success! File saved as:")
            print(f"📁 {expected_filename}")
            print(f"📏 Size: {os.path.getsize(expected_filename) / (1024*1024):.2f} MB")
            return expected_filename
        else:
            print(f"\n⚠️  File not found at expected location: {expected_filename}")
            # Try to find it
            found_file = find_downloaded_file(video_title, output_path)
            if not found_file:
                # Search in current directory and parent directories
                find_downloaded_file(video_title, os.path.dirname(output_path))
            return found_file
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

def simple_download():
    """Simple command-line download without menu"""
    print("=" * 60)
    print("YouTube to MP3 Downloader (Simple Version)")
    print("=" * 60)
    
    # Check dependencies
    try:
        import yt_dlp
    except ImportError:
        print("Please install yt-dlp first:")
        print("pip install yt-dlp")
        return
    
    url = input("\nEnter YouTube URL: ").strip()
    if not url:
        print("No URL provided.")
        return
    
    print("\nOptions:")
    print("1. High quality (320kbps)")
    print("2. Good quality (192kbps) [Default]")
    print("3. Standard quality (128kbps)")
    
    choice = input("Select quality (1-3) [2]: ").strip()
    quality_map = {"1": "320", "2": "192", "3": "128"}
    quality = quality_map.get(choice, "192")
    
    print("\nOptions:")
    print("1. Save to default Downloads folder")
    print("2. Save to current directory")
    print("3. Choose custom folder")
    
    location_choice = input("Select location (1-3) [1]: ").strip()
    
    if location_choice == "2":
        output_path = os.getcwd()
    elif location_choice == "3":
        output_path = input("Enter folder path: ").strip()
        if not os.path.exists(output_path):
            print(f"Creating folder: {output_path}")
            os.makedirs(output_path, exist_ok=True)
    else:
        output_path = get_default_download_path()
    
    print(f"\n📁 Saving to: {output_path}")
    print(f"🎵 Quality: {quality}kbps")
    print("-" * 60)
    
    result = download_youtube_as_mp3(url, output_path, quality)
    
    if result:
        print("\n🎉 Download completed successfully!")
        
        # Try to open the folder
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(os.path.dirname(result))
            elif system == "Darwin":  # macOS
                os.system(f'open "{os.path.dirname(result)}"')
            else:  # Linux
                os.system(f'xdg-open "{os.path.dirname(result)}"')
        except:
            pass
    else:
        print("\n❌ Download failed.")

def list_recent_downloads():
    """List recently downloaded MP3 files"""
    download_path = get_default_download_path()
    
    print(f"\n📁 Recent downloads in: {download_path}")
    print("-" * 60)
    
    mp3_files = []
    for file in os.listdir(download_path):
        if file.lower().endswith('.mp3'):
            file_path = os.path.join(download_path, file)
            file_size = os.path.getsize(file_path) / (1024*1024)  # MB
            mp3_files.append((file, file_size))
    
    if mp3_files:
        for i, (filename, size) in enumerate(sorted(mp3_files, key=lambda x: os.path.getctime(os.path.join(download_path, x[0])), reverse=True)[:10], 1):
            print(f"{i}. {filename} ({size:.2f} MB)")
    else:
        print("No MP3 files found.")
    
    print("-" * 60)

if __name__ == "__main__":
    # Run the simple version
    simple_download()
    
    # List recent downloads
    list_recent_downloads()
    
    input("\nPress Enter to exit...")