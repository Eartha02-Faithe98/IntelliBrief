import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def fetch_google_news(keyword: str, max_results: int = 10) -> list:
    """
    透過 RSS 抓取 Google News 特定關鍵字的新聞標題與連結。
    """
    encoded_keyword = quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    try:
        feed = feedparser.parse(rss_url)
        news_list = []
        for entry in feed.entries[:max_results]:
            news_list.append({
                'title': entry.title,
                'url': entry.link,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                'published_at': entry.published if hasattr(entry, 'published') else None,
                'category': keyword
            })
        return news_list
    except Exception as e:
        print(f"抓取 {keyword} 的 Google News 失敗: {e}")
        return []

def extract_article_content(url: str, timeout: int = 10) -> str:
    """
    爬取新聞原始連結的正文內容。
    加入 timeout 避免長時間阻塞。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 允許 redirect
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 簡單策略：抓取所有 <p> 標籤的文字
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if not content:
            # 若無 <p> 標籤，退而求其次抓取整個 body 或提示
            return "(無法自動提取正文內容，可能為動態網頁或格式特殊，請點擊連結閱讀原文)"
            
        return content
    except requests.exceptions.Timeout:
        return "(連線超時：無法提取正文)"
    except requests.exceptions.RequestException as e:
        return f"(請求失敗：{e})"
    except Exception as e:
        return f"(提取內文發生未預期錯誤：{e})"
