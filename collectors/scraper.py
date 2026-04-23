import requests
from bs4 import BeautifulSoup
from core.db import save_raw_content
from urllib.parse import urljoin, urlparse

def collect_scraper(urls_with_limits):
    """Scraper that uses the registered display name and preserves sub-categories in titles."""
    all_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for item in urls_with_limits:
        base_url = item['url']
        limit = item['limit']
        display_name = item['display_name']
        
        main_domain = ".".join(urlparse(base_url).netloc.split('.')[-2:])
        
        print(f"🔍 Scraping {display_name}: {base_url} (limit: {limit})")
        
        try:
            response = requests.get(base_url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links_found = 0
            seen_urls = set()
            seen_titles = set()

            for a_tag in soup.find_all('a', href=True):
                url = urljoin(base_url, a_tag.get('href'))
                title = " ".join(a_tag.get_text().strip().split())
                
                if url in seen_urls or title in seen_titles: continue
                
                # HEURISTICS FOR A PORTAL NEWS LINK:
                # 1. Title must be substantial
                # 2. Link must belong to the same main domain
                # 3. Avoid obvious menu/utility/social links and portal-specific service ads
                forbidden_words = [
                    'login', 'assine', 'termos', 'privacidade', 'account', 'subscribe', 
                    'newsletter', 'facebook', 'twitter', 'linkedin', 'uolplay', 
                    'uolmail', 'pagbank', 'uol-afiliados', 'bate-papo', 'shopping',
                    'patrocinado', 'web-stories', 'ofertas', 'promocao'
                ]
                
                is_valid_portal_link = (
                    len(title) > 28 and 
                    main_domain in urlparse(url).netloc and
                    not any(word in url.lower() for word in forbidden_words)
                )

                if is_valid_portal_link:
                    # Try to find category context
                    category_label = ""
                    # Enhanced category detection: look for nearby links with specific classes or small text
                    container = a_tag.find_parent(['div', 'article', 'section'])
                    if container:
                        # TechCrunch and others often put category in a specific span or small link above
                        label_tag = container.find(['span', 'a'], class_=lambda x: x and ('category' in x or 'kicker' in x))
                        if not label_tag:
                            label_tag = a_tag.find_previous(['span', 'a'])
                        
                        if label_tag:
                            lbl = label_tag.get_text().strip().upper()
                            if 2 < len(lbl) < 20 and lbl != title.upper():
                                category_label = lbl

                    # Final title includes the label for context
                    final_title = f"[{category_label}] {title}" if category_label else title
                    
                    all_items.append({
                        "source": f"Scraper: {display_name}",
                        "title": final_title,
                        "url": url,
                        "content": "", 
                        "published_at": None
                    })
                    
                    seen_urls.add(url)
                    seen_titles.add(title)
                    links_found += 1
                    if links_found >= limit:
                        break
                            
        except Exception as e:
            print(f"Error scraping {base_url}: {e}")

    if all_items:
        save_raw_content(all_items)
        print(f"✅ Scraper saved {len(all_items)} items for {display_name}.")
