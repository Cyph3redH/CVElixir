import requests
from bs4 import BeautifulSoup

DANGER_KEYWORDS = ['CVE', '0-day', 'RCE', 'critical', 'exploit', 'Zero-Day']

def is_dangerous(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in DANGER_KEYWORDS)

def fetch_dangerous_articles():
    url = "https://thehackernews.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = soup.find_all('div', class_='body-post')
    dangerous_articles = []
    
    for article in articles:
        title_tag = article.find('h2', class_='home-title')
        if not title_tag:
            continue
            
        title_text = title_tag.text.strip()
        if is_dangerous(title_text):
            link_tag = article.find('a', class_='story-link')
            link = link_tag.get('href') if link_tag else None
            
            dangerous_articles.append({
                'title': title_text,
                'link': link
            })
    return dangerous_articles