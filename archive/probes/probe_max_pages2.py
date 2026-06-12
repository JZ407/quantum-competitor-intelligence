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

def get_flash_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    box = soup.find('div', class_='flash-box') or soup.find('div', class_='flash-list')
    if not box:
        return []
    return [m.group(1) for a in box.find_all('a', href=re.compile(r'/flash/\d+\.html'))
            if (m := re.search(r'/flash/(\d+)\.html', a['href']))]

def get_reference_ids(html):
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    box = soup.find('div', class_='term-list') or soup.find('div', class_='item-list')
    if not box:
        return []
    return [m.group(1) for a in box.find_all('a', href=re.compile(r'/reference/\d+\.html'))
            if (m := re.search(r'/reference/(\d+)\.html', a['href']))]

def find_exact_max(path, extractor, label, low, high):
    """Binary search for exact max page between low and high"""
    out = [f'=== Exact max for {label} ===']
    # Check high first
    url = f'{BASE_URL}{path}?page={high}'
    ids = extractor(fetch(url))
    if ids:
        out.append(f'Page {high} still has content, need to search higher')
        return '\n'.join(out)

    # Binary search
    best = low
    while low <= high:
        mid = (low + high) // 2
        url = f'{BASE_URL}{path}?page={mid}'
        ids = extractor(fetch(url))
        has_content = len(ids) > 0
        out.append(f'page={mid}: {len(ids)} articles')
        if has_content:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    out.append(f'Max valid page: {best}')
    return '\n'.join(out)

results = []
results.append(find_exact_max('/news', get_news_ids, '/news', 20, 40))
results.append('')
results.append(find_exact_max('/flash', get_flash_ids, '/flash', 400, 520))
results.append('')
results.append(find_exact_max('/reference', get_reference_ids, '/reference', 20, 40))

with open('probe_max_pages2_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print('Saved to probe_max_pages2_report.txt')
