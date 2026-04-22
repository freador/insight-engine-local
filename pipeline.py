from core.db import init_db, get_sources
from core.refiner import refine_content
from collectors.rss import collect_rss
from collectors.youtube import collect_youtube
from collectors.scraper import collect_scraper

def run_pipeline():
    print("--- Starting InsightEngine Pipeline ---")
    
    # 1. Initialize Database
    print("Initializing Database...")
    init_db()
    
    # 2. Get Sources from DB
    db_sources = get_sources()
    
    if not db_sources:
        print("⚠️ No sources found in database. Add some via the web interface!")
        return

    # Organize sources by type for efficient collection
    # We pass the official 'name' (if exists) or a clean version of the URL
    rss_list = []
    yt_list = []
    scraper_list = []

    for s in db_sources:
        # Determine a clean display name if none provided
        if s.name:
            display_name = s.name
        elif "@" in s.url: # Capture @Handle for YouTube
            display_name = s.url.split("@")[-1].split('/')[0]
            display_name = f"@{display_name}"
        else:
            display_name = s.url.split('//')[-1].split('/')[0].replace('www.', '')
        
        source_info = {
            "url": s.url, 
            "limit": s.item_limit,
            "display_name": display_name
        }
        
        if s.type == 'RSS': rss_list.append(source_info)
        elif s.type == 'YouTube': yt_list.append(source_info)
        elif s.type == 'Scraper': scraper_list.append(source_info)

    # 3. Run Collectors
    print(f"\nRunning Collectors ({len(db_sources)} sources)...")
    if rss_list:
        collect_rss(rss_list)
    if yt_list:
        collect_youtube(yt_list)
    if scraper_list:
        collect_scraper(scraper_list)
    
    # 4. Run Refiner
    print("\nRunning Intelligence Refinement...")
    refine_content()
    
    print("\n--- Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_pipeline()
