import pickle, requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, parse_qs, urlparse

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

def analyze_list_page(url, label, out_lines):
    out_lines.append(f'\n===== Analyzing {label}: {url} =====')
    html = fetch(url)
    if not html:
        out_lines.append('Fetch failed')
        return
    soup = BeautifulSoup(html, 'html.parser')

    # Find pagination elements
    pagination = soup.find_all(['div', 'ul', 'nav'], class_=re.compile(r'page|pagination|pager|pages', re.I))
    out_lines.append(f'Pagination blocks found: {len(pagination)}')
    for i, p in enumerate(pagination[:3]):
        out_lines.append(f'--- Block {i} ---')
        text = p.get_text(separator=' | ', strip=True)[:500]
        out_lines.append(text)
        for a in p.find_all('a', href=True):
            out_lines.append(f'  LINK: {a.get_text(strip=True)!r} -> {urljoin(BASE_URL, a["href"])}')

    # Look for numeric navigation links
    all_links = soup.find_all('a', href=True)
    num_links = []
    for a in all_links:
        text = a.get_text(strip=True)
        href = a['href']
        if text.isdigit() or text in ['下一页', '上一页', 'Next', 'Previous', '首页', '尾页', '>>', '<<', '...']:
            num_links.append((text, urljoin(BASE_URL, href)))
    if num_links:
        out_lines.append('--- Numeric / Navigation links ---')
        for text, href in num_links[:20]:
            out_lines.append(f'  {text!r:10} -> {href}')

    # Extract article links
    article_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href and ('/news/' in href or '/article/' in href or '/flash/' in href or '/reference/' in href):
            full = urljoin(BASE_URL, href)
            path = urlparse(full).path
            if re.search(r'/(news|article|flash|reference)/\d', path):
                if full not in article_links:
                    article_links.append(full)

    out_lines.append(f'Article links on this page: {len(article_links)}')
    for url in article_links[:5]:
        out_lines.append(f'  {url}')

    # Save HTML
    with open(f'probe_{label.replace("/","_")}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    out_lines.append(f'Saved HTML to probe_{label.replace("/","_")}.html')
    return soup

out = []
analyze_list_page(BASE_URL + '/news', '/news', out)
analyze_list_page(BASE_URL + '/flash', '/flash', out)

test_urls = [
    BASE_URL + '/news?page=1',
    BASE_URL + '/news?page=2',
    BASE_URL + '/news?p=2',
    BASE_URL + '/news?offset=20',
    BASE_URL + '/news?pageSize=20',
]
out.append('\n===== Testing common pagination params =====')
for u in test_urls:
    r = session.get(u, headers=headers, timeout=10, allow_redirects=True)
    out.append(f'{u}: status={r.status_code}, final={r.url}, len={len(r.text)}')

with open('probe_pagination_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Report saved to probe_pagination_report.txt')
