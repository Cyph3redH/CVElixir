import requests
from bs4 import BeautifulSoup

def is_critical(score):
    return score >= 9.0

def search_critical_cve():
    url = "https://nvd.nist.gov/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    list_items = soup.find_all('li')

    critical_cve = []
    found_cve_blocks = 0

    for li in list_items:

        right_col = li.find('div', class_='col-lg-3')
        left_col = li.find('div', class_='col-lg-9')
        # Парсинг вектора
        # cvss_link = li.find('a', {'data-testid': re.compile(r'vuln-cvss3-link-\d+')})
        # vector = None
        # if cvss_link:
        # href = cvss_link.get('href')
        # parsed = urlparse(href)
        # params = parse_qs(parsed.query)
        # vector = params.get('vector', [None])[0]

        if not right_col or not left_col:
            continue

        found_cve_blocks += 1

        tag_critical = right_col.find('a', class_='label label-critical')
        if not tag_critical:
            continue

        full_text = tag_critical.text.strip()
        score_str = full_text.split()[0]

        try:
            score = float(score_str)
        except ValueError:
            continue

        if not is_critical(score):
            continue
        
        left_col = li.find('div', class_='col-lg-9')
        if not left_col:
            continue

        strong_tag = left_col.find('strong')
        if not strong_tag:
            continue

        link_tag = strong_tag.find('a')
        if not link_tag:
            continue

        cve_id = link_tag.text.strip()
        link = link_tag.get('href')
        full_url = f"https://nvd.nist.gov{link}" if link.startswith('/') else link

        critical_cve.append({
            'cve_id': cve_id,
            'cvss': score,
            'link': full_url,
            # 'vector': vector
        })
    return critical_cve