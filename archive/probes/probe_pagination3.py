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

def get_main_article_ids(html):
    """Extract article IDs from the main news list only (not sidebar)"""
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    # Find the main news list container
    news_list = soup.find('div', class_='news-list')
    if not news_list:
        return []
    ids = []
    for a in news_list.find_all('a', href=re.compile(r'/(article|flash|reference)/\d+\.html')):
        href = a['href']
        m = re.search(r'/(article|flash|reference)/(\d+)\.html', href)
        if m:
            ids.append(m.group(2))
    return ids

out = []
for page in [0, 1, 2, 5, 10]:
    url = f'{BASE_URL}/news?page={page}'
    html = fetch(url)
    ids = get_main_article_ids(html)
    out.append(f'/news?page={page}: {len(ids)} articles, IDs={ids[:5]}')

out.append('')
for page in [0, 1, 2, 5, 10]:
    url = f'{BASE_URL}/flash?page={page}'
    html = fetch(url)
    ids = get_main_article_ids(html)
    out.append(f'/flash?page={page}: {len(ids)} articles, IDs={ids[:5]}')

out.append('')
for page in [0, 1, 2, 5, 10]:
    url = f'{BASE_URL}/reference?page={page}'
    html = fetch(url)
    ids = get_main_article_ids(html)
    out.append(f'/reference?page={page}: {len(ids)} articles, IDs={ids[:5]}')

with open('probe_pagination3_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Saved to probe_pagination3_report.txt')
