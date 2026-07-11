import requests
from bs4 import BeautifulSoup
import json
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_homepage(url: str) -> tuple[str, BeautifulSoup]:
    """Fetches and parses the homepage HTML once."""
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            return resp.text, BeautifulSoup(resp.text, 'lxml')
    except Exception as e:
        logger.error(f"[HTML Extractor] Failed to fetch {url}: {e}")
    return "", None

def get_favicon(soup: BeautifulSoup, base_url: str) -> str:
    """Tier 2: Favicon"""
    if not soup: return ""
    tags = [
        soup.find("link", rel=lambda x: x and 'icon' in x.lower()),
        soup.find("link", rel=lambda x: x and 'apple-touch-icon' in x.lower()),
        soup.find("link", rel=lambda x: x and 'shortcut icon' in x.lower())
    ]
    for tag in tags:
        if tag and tag.get('href'):
            href = tag.get('href')
            if 'favicon' in href.lower() or 'logo' in href.lower() or 'icon' in href.lower():
                return urljoin(base_url, href)
    return ""

def get_og_image(soup: BeautifulSoup, base_url: str) -> str:
    """Tier 3: Open Graph Image"""
    if not soup: return ""
    tags = [
        soup.find("meta", property="og:image"),
        soup.find("meta", attrs={"name": "twitter:image"})
    ]
    for tag in tags:
        if tag and tag.get('content'):
            return urljoin(base_url, tag.get('content'))
    return ""

def get_json_ld_logo(soup: BeautifulSoup, base_url: str) -> str:
    """Tier 4: JSON-LD Structured Data"""
    if not soup: return ""
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        if not script.string: continue
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                # Check for logo directly
                if 'logo' in data:
                    logo = data['logo']
                    if isinstance(logo, str): return urljoin(base_url, logo)
                    if isinstance(logo, dict) and 'url' in logo: return urljoin(base_url, logo['url'])
                # Or check if it's CollegeOrUniversity and has an image
                if data.get('@type') in ['CollegeOrUniversity', 'EducationalOrganization', 'Organization']:
                    if 'image' in data:
                        img = data['image']
                        if isinstance(img, str): return urljoin(base_url, img)
                        if isinstance(img, dict) and 'url' in img: return urljoin(base_url, img['url'])
        except json.JSONDecodeError:
            continue
    return ""

def get_header_logo(soup: BeautifulSoup, base_url: str) -> str:
    """Tier 5: Official Website Header Logo (incl. CSS background)"""
    if not soup: return ""
    
    headers = soup.find_all(['header', 'nav', 'div'], class_=lambda x: x and ('header' in x.lower() or 'nav' in x.lower() or 'logo' in x.lower()))
    if not headers:
        headers = [soup] # Fallback to whole page
        
    import re
    bg_regex = re.compile(r'url\([\'"]?([^\'"]+?)[\'"]?\)')
        
    for header in headers:
        # Search by specific classes first
        img = header.find("img", class_=lambda x: x and any(c in x.lower() for c in ['logo', 'brand', 'site-logo']))
        if img and img.get('src'):
            return urljoin(base_url, img.get('src'))
            
        # Fallback to id
        img = header.find("img", id=lambda x: x and 'logo' in x.lower())
        if img and img.get('src'):
            return urljoin(base_url, img.get('src'))
            
        # Fallback to any image with 'logo' in src
        imgs = header.find_all("img")
        for i in imgs:
            if i.get('src') and 'logo' in i.get('src').lower():
                return urljoin(base_url, i.get('src'))
                
        # CSS Background Image check
        for tag in header.find_all(style=True):
            style = tag.get('style', '')
            if 'background' in style.lower():
                match = bg_regex.search(style)
                if match:
                    bg_url = match.group(1)
                    if 'logo' in bg_url.lower():
                        return urljoin(base_url, bg_url)
                
    return ""
