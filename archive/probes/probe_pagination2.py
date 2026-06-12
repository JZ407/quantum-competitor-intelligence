import pickle, requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'http://www.qtc.com.cn'
COOKIE_PATH = './cookies/qtc_cookies.pkl'

try:
    with open(COOKIE_PATH, 'rb') as f:
        cookies = pickle.load(f)
except Exception as e:
    print('Cookie load failed:', e)
    exit(1)

session = requests.Session()
if isinstance(cookies, dict):
    for k, v in cookies.items():
        session.cookies.set(k, v)
else:
    for c in cookies:
        session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path'))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': BASE_URL + '/',
}

def fetch(url):
    try:
        r = session.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or 'utf-8'
        return r.text
    except Exception as e:
        return None

def count_articles(html):
    if not html:
        return 0
    soup = BeautifulSoup(html, 'html.parser')
    # article links with numeric IDs
    links = soup.find_all('a', href=re.compile(r'/(article|flash|reference)/\d+\.html'))
    unique = set()
    for a in links:
        href = a['href']
        if href.startswith('/'):
            unique.add(href)
    return len(unique)

out = []

# Probe /news pages to find max
out.append('=== Probing /news max pages ===')
for page in [0, 1, 5, 10, 20, 50, 100, 200, 500, 1000]:
    url = f'{BASE_URL}/news?page={page}'
    html = fetch(url)
    cnt = count_articles(html) if html else 0
    status = 'OK' if html else 'FAIL'
    out.append(f'page={page:4}: {status}, articles={cnt}')
    if not html or cnt == 0:
        out.append(f'  -> Empty or failed at page {page}, likely end')
        break

# Probe /flash
out.append('\n=== Probing /flash pages ===')
for page in [0, 1, 5, 10, 20, 50, 100]:
    url = f'{BASE_URL}/flash?page={page}'
    html = fetch(url)
    cnt = count_articles(html) if html else 0
    status = 'OK' if html else 'FAIL'
    out.append(f'page={page:4}: {status}, articles={cnt}')
    if not html or cnt == 0:
        out.append(f'  -> Empty or failed at page {page}')
        break

# Probe /reference
out.append('\n=== Probing /reference pages ===')
for page in [0, 1, 5, 10, 20, 50, 100]:
    url = f'{BASE_URL}/reference?page={page}'
    html = fetch(url)
    cnt = count_articles(html) if html else 0
    status = 'OK' if html else 'FAIL'
    out.append(f'page={page:4}: {status}, articles={cnt}')
    if not html or cnt == 0:
        out.append(f'  -> Empty or failed at page {page}')
        break

# Also try /reference/arxiv
url = f'{BASE_URL}/reference/arxiv'
html = fetch(url)
cnt = count_articles(html) if html else 0
out.append(f'\n/reference/arxiv: articles={cnt}')

with open('probe_pagination2_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Saved to probe_pagination2_report.txt')
