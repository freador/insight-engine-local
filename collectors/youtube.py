import yt_dlp
from core.db import save_raw_content
from datetime import datetime

def collect_youtube(channels_with_limits):
    """Collect YouTube videos using the registered display name."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }
    
    all_items = []
    
    for item in channels_with_limits:
        url = item['url']
        limit = item['limit']
        display_name = item['display_name']
        
        # Smart URL Completion: Ensure we go to the /videos page for better results
        if "youtube.com/@" in url and not url.endswith("/videos"):
            url = url.rstrip('/') + "/videos"
        elif "youtube.com/channel/" in url and not url.endswith("/videos"):
            url = url.rstrip('/') + "/videos"
        elif "youtube.com/user/" in url and not url.endswith("/videos"):
            url = url.rstrip('/') + "/videos"
            
        print(f"Fetching YouTube: {display_name} (using {url})")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    entries = list(info['entries'])[:limit]
                    for entry in entries:
                        all_items.append({
                            "source": f"YouTube: {display_name}",
                            "title": entry.get('title'),
                            "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                            "content": entry.get('description', ''),
                            "published_at": datetime.now()
                        })
        except Exception as e:
            print(f"Error collecting YouTube {url}: {e}")

    if all_items:
        save_raw_content(all_items)
        print(f"Saved {len(all_items)} YouTube items.")
