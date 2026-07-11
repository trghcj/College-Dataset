import time
import logging
import urllib.parse
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException

logger = logging.getLogger(__name__)

IGNORE_KEYWORDS = [
    'wikipedia.org', 'careers360.com', 'collegedunia.com', 'shiksha.com',
    'getmyuni.com', 'collegedekho.com', 'linkedin.com', 'facebook.com',
    'instagram.com', 'twitter.com', 'youtube.com', 'justdial.com',
    'indiatoday.in', 'news', 'blog', 'indianculture.gov.in',
    'aicte-india.org', 'ugc.ac.in', 'mhrd.gov.in', 'nirfindia.org',
    'education.gov.in', 'nba-india.org', 'india.gov.in', 'netflix', 'microsoft',
    'apple', 'google', 'flag', 'emblem', 'reddit', 'byju', 'host', 'medium', 'quora', 'pinterest',
    'glassdoor', 'ambitionbox', 'naukri', 'indeed', 'mouthshut', 'justdial',
    'wordpress', 'blogspot', 'wix', 'weebly', 'site123', 'squarespace', 'netlify', 'vercel'
]

def extract_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
    except Exception:
        return ""

def is_ignored(url: str) -> bool:
    url_lower = url.lower()
    domain = extract_domain(url_lower)
    for kw in IGNORE_KEYWORDS:
        if kw in url_lower or kw in domain:
            return True
    return False

def get_domain_priority(domain: str) -> int:
    if domain.endswith('.ac.in'):
        return 1
    elif domain.endswith('.edu.in'):
        return 2
    elif domain.endswith('.edu'):
        return 3
    elif domain.endswith('.org.in') or domain.endswith('.res.in') or domain.endswith('.ernet.in') or domain.endswith('.gov.in'):
        return 4
    return 99

import threading

search_lock = threading.Lock()

def search_official_website(college_name: str, max_retries: int = 3) -> str:
    query = f"{college_name} official website"
    
    for attempt in range(max_retries):
        try:
            with search_lock:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=15))
                
                valid_urls = []
                for res in results:
                    url = res.get('href', '')
                    if url and not is_ignored(url):
                        valid_urls.append(url)
                
                if not valid_urls:
                    print(f"DEBUG: No valid urls for {query}")
                    return ""
                    
                # Rank valid URLs based on domain priority
                ranked_urls = []
                for url in valid_urls:
                    domain = extract_domain(url)
                    priority = get_domain_priority(domain)
                    print(f"DEBUG: Domain {domain} priority {priority}")
                    if priority < 99:
                        ranked_urls.append((priority, url))
                    
                if not ranked_urls:
                    print(f"DEBUG: No ranked urls for {query}")
                    continue
                    
                # Sort by priority
                ranked_urls.sort(key=lambda x: x[0])
                
                # Return the best match
                print(f"DEBUG: Best match for {query}: {ranked_urls[0][1]}")
                return ranked_urls[0][1]
                
        except RatelimitException:
            logger.warning(f"DDGS Rate limit hit for {college_name}. Retrying ({attempt+1}/{max_retries})...")
            time.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"Error searching for {college_name}: {e}")
            time.sleep(1)
            
    return ""

def search_github_logo(college_name: str, max_retries: int = 2) -> str:
    """Tier 7: Search GitHub for logo files."""
    query = f"site:github.com {college_name} logo.png"
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                for res in results:
                    url = res.get('href', '')
                    if url and 'github.com' in url and url.endswith('.png'):
                        return url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        except Exception as e:
            time.sleep(1)
    return ""

def search_filetype(college_name: str, filetype: str, max_retries: int = 2) -> str:
    """Tier 8: Exact filetype search."""
    query = f"{college_name} logo filetype:{filetype}"
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                for res in results:
                    url = res.get('href', '')
                    if url and url.lower().endswith(f".{filetype}"):
                        return url
        except Exception as e:
            time.sleep(1)
    return ""

def search_ddg_image(college_name: str, max_retries: int = 2) -> str:
    """Tier 10: DuckDuckGo Image Search Fallback"""
    query = f"{college_name} logo"
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                # We specifically look for images with "logo" in the filename/url to avoid event photos
                results = list(ddgs.images(query, max_results=10))
                for res in results:
                    url = res.get('image', '')
                    if url and not any(kw in url.lower() for kw in IGNORE_KEYWORDS):
                        if 'logo' in url.lower() or url.lower().endswith(('.svg', '.png')):
                            return url
        except Exception as e:
            time.sleep(1)
    return ""
