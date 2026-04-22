import requests
from bs4 import BeautifulSoup

"""===Парсер CVSS от переданной CVE==="""

def search_CVSS_CVE(cve):
    url = f"https://nvd.nist.gov/vuln/detail/{cve}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

# 4.0 ===================================================================================================

    # 1. Ищем ВИДИМУЮ панель 4.0
    panel4 = soup.find('div', id='Vuln4CvssPanel')
    if panel4 and 'display: none' not in panel4.get('style', ''):
        title_tag = panel4.find('a', attrs={'data-testid': 'vuln-cvss4-panel-score'})
        if not title_tag:
            title_tag = panel4.find('a', attrs={'data-testid': 'vuln-cvss4-panel-score-na'})
        if title_tag:
            score_text = title_tag.text.strip()
            if score_text.upper() != 'N/A':
                return float(score_text.split()[0])
# 4.0 end===================================================================================================


# 3.x ===================================================================================================

    articles = soup.find_all('div', id='Vuln3CvssPanel')

    panel3 = soup.find('div', id='Vuln3CvssPanel')
    if panel3:
        # Ищем NIST-оценку
        score_tag = panel3.find('a', attrs={'data-testid': 'vuln-cvss3-panel-score'})
        if not score_tag:
            # Ищем CNA-оценку
            score_tag = panel3.find('a', attrs={'data-testid': 'vuln-cvss3-cna-panel-score'})
        if not score_tag:
            score_tag = panel3.find('a', attrs={'data-testid': 'vuln-cvss3-panel-score-na'})
        if not score_tag:
            score_tag = panel3.find('a', class_='label label-critical')
        if not score_tag:
            score_tag = panel3.find('a', class_='label label-warning')
        
        if score_tag:
            score_text = score_tag.text.strip()
            if score_text.upper() != 'N/A':
                return float(score_text.split()[0])
        else:
            return None


# 3.0 end ===================================================================================================

# Запасной вариант ===================================================================================================
    for article in articles:
        title_tag = article.find('a', attrs={'data-testid': 'vuln-cvss3-panel-score'})
        if not title_tag:
            title_tag = article.find('a', attrs={'data-testid': 'vuln-cvss3-panel-score-na'})
        if not title_tag:
            title_tag = article.find('a', class_='label label-critical')
        if title_tag:
            score_text = title_tag.text.strip()
            if score_text.upper() != 'N/A':
                return float(score_text.split()[0])

    return None

# if __name__ == "__main__":
#     score = search_CVSS_CVE("CVE-2026-35197")
#     print(f"\nРезультат: {score}")