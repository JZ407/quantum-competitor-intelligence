import pickle, requests, re
from bs4 import BeautifulSoup

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

def get_news_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    news_list = soup.find('div', class_='news-list')
    if not news_list:
        return []
    return [m.group(1) for a in news_list.find_all('a', href=re.compile(r'/article/\d+\.html'))
            if (m := re.search(r'/article/(\d+)\.html', a['href']))]

def get_reference_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    box = soup.find('div', class_='term-list') or soup.find('div', class_='item-list')
    if not box:
        return []
    return [m.group(1) for a in box.find_all('a', href=re.compile(r'/reference/\d+\.html'))
            if (m := re.search(r'/reference/(\d+)\.html', a['href']))]

out = []
for page in [500, 600, 700, 800, 900, 1000, 1200, 1500]:
    url = f'{BASE_URL}/news?page={page}'
    ids = get_news_ids(fetch(url))
    out.append(f'/news?page={page}: {len(ids)} articles')
    if not ids:
        break

out.append('')
for page in [500, 600, 700, 800, 900, 1000, 1200, 1500]:
    url = f'{BASE_URL}/reference?page={page}'
    ids = get_reference_ids(fetch(url))
    out.append(f'/reference?page={page}: {len(ids)} articles')
    if not ids:
        break

with open('probe_quick_max_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Saved to probe_quick_max_report.txt')
