import requests
from bs4 import BeautifulSoup
from core.db import save_raw_content
from urllib.parse import urljoin

def collect_github(urls_with_limits):
    """Specialized collector for GitHub Trending pages."""
    all_items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for item in urls_with_limits:
        url = item['url']
        limit = item['limit']
        display_name = item['display_name']
        
        print(f"🚀 Collecting GitHub Trending: {url} (limit: {limit})")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # GitHub Trending items are in <article class="Box-row">
            repos = soup.find_all('article', class_='Box-row')
            
            for i, repo in enumerate(repos):
                if i >= limit:
                    break
                
                # Extract Title & Link
                h2 = repo.find('h2', class_='h3')
                if not h2: continue
                a_tag = h2.find('a')
                if not a_tag: continue
                
                repo_name = a_tag.get_text().strip().replace('\n', '').replace(' ', '')
                repo_url = urljoin("https://github.com", a_tag.get('href'))
                
                # Extract Description
                p = repo.find('p', class_='col-9')
                description = p.get_text().strip() if p else "No description provided."
                
                # Extract Language
                lang_tag = repo.find('span', itemprop='programmingLanguage')
                language = lang_tag.get_text().strip() if lang_tag else "N/A"
                
                # Extract Stars
                stars_tag = repo.find('a', href=lambda x: x and 'stargazers' in x)
                stars = stars_tag.get_text().strip() if stars_tag else "0"

                all_items.append({
                    "source": f"GitHub: {display_name}",
                    "title": f"Trending: {repo_name} ({language})",
                    "url": repo_url,
                    "content": f"Language: {language} | Stars: {stars} | Description: {description}",
                    "published_at": None
                })
                            
        except Exception as e:
            print(f"Error collecting GitHub {url}: {e}")

    if all_items:
        save_raw_content(all_items)
        print(f"✅ GitHub Collector saved {len(all_items)} trending repositories.")

if __name__ == "__main__":
    collect_github([{"url": "https://github.com/trending", "limit": 5, "display_name": "Daily"}])
