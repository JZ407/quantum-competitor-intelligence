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
    ids = []
    for a in news_list.find_all('a', href=re.compile(r'/article/\d+\.html')):
        m = re.search(r'/article/(\d+)\.html', a['href'])
        if m:
            ids.append(m.group(1))
    return ids

def get_flash_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    box = soup.find('div', class_='flash-box') or soup.find('div', class_='flash-list')
    if not box:
        return []
    ids = []
    for a in box.find_all('a', href=re.compile(r'/flash/\d+\.html')):
        m = re.search(r'/flash/(\d+)\.html', a['href'])
        if m:
            ids.append(m.group(1))
    return ids

def get_reference_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    box = soup.find('div', class_='term-list') or soup.find('div', class_='item-list')
    if not box:
        return []
    ids = []
    for a in box.find_all('a', href=re.compile(r'/reference/\d+\.html')):
        m = re.search(r'/reference/(\d+)\.html', a['href'])
        if m:
            ids.append(m.group(1))
    return ids

def find_max_pages(path, extractor, label):
    out = [f'=== Finding max pages for {label} ===']
    # Exponential search first
    page = 1
    last_valid_ids = []
    while True:
        url = f'{BASE_URL}{path}?page={page}'
        html = fetch(url)
        ids = extractor(html)
        out.append(f'page={page}: {len(ids)} articles, first={ids[:2] if ids else "EMPTY"}')
        if not ids or (last_valid_ids and ids == last_valid_ids):
            out.append(f'  -> Empty or duplicate at page {page}')
            break
        last_valid_ids = ids
        page *= 2
        if page > 10000:
            out.append('  -> Reached safety limit')
            break

    # Now binary search between page//2 and page
    low = page // 4 if page > 1 else 0
    high = page if page > 1 else 1
    out.append(f'Binary search range: {low} - {high}')

    # Actually, simpler: just check pages around the boundary
    for p in [low, low + (high-low)//2, high-1, high, high+1]:
        url = f'{BASE_URL}{path}?page={p}'
        html = fetch(url)
        ids = extractor(html)
        out.append(f'  check page={p}: {len(ids)} articles')

    return '\n'.join(out)

results = []
results.append(find_max_pages('/news', get_news_ids, '/news'))
results.append('')
results.append(find_max_pages('/flash', get_flash_ids, '/flash'))
results.append('')
results.append(find_max_pages('/reference', get_reference_ids, '/reference'))

with open('probe_max_pages_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print('Saved to probe_max_pages_report.txt')
