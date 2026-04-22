import feedparser
from core.db import save_raw_content
from datetime import datetime
import time

def collect_rss(feeds_with_limits):
    """Collect RSS items using the registered display name."""
    all_items = []
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    for feed_item in feeds_with_limits:
        url = feed_item['url']
        limit = feed_item['limit']
        display_name = feed_item['display_name']
        
        print(f"Fetching RSS: {display_name} (limit: {limit})")
        feed = feedparser.parse(url, agent=USER_AGENT)
        
        count = 0
        for entry in feed.entries:
            if count >= limit:
                break
            
            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            
            all_items.append({
                "source": display_name,
                "title": entry.title,
                "url": entry.link,
                "content": entry.summary if hasattr(entry, 'summary') else entry.get('description', ''),
                "published_at": published
            })
            count += 1
    
    if all_items:
        save_raw_content(all_items)
        print(f"Saved {len(all_items)} RSS items.")
