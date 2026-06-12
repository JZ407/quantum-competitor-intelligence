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

def analyze_page_structure(url, label):
    html = fetch(url)
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    # Find containers that hold article links
    containers = soup.find_all(['div', 'ul'], class_=re.compile(r'news|flash|reference|list', re.I))
    out = [f'=== {label} ===']
    out.append(f'Total containers matching news/flash/reference/list: {len(containers)}')
    for i, c in enumerate(containers[:5]):
        cls = c.get('class', [])
        article_links = []
        for a in c.find_all('a', href=re.compile(r'/(article|flash|reference)/\d+\.html')):
            m = re.search(r'/(article|flash|reference)/(\d+)\.html', a['href'])
            if m:
                article_links.append(m.group(2))
        out.append(f'  container {i} class={cls}: {len(article_links)} article links, first few={article_links[:3]}')
    with open(f'probe_structure_{label.replace("/","_")}.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'Saved probe_structure_{label.replace("/","_")}.txt')

analyze_page_structure(f'{BASE_URL}/flash', '/flash')
analyze_page_structure(f'{BASE_URL}/reference', '/reference')
analyze_page_structure(f'{BASE_URL}/reference/arxiv', '/reference/arxiv')
