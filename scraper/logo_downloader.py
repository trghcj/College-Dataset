import os
import re
import requests
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ['.png']
REJECTED_FORMATS = ['.ico', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.jpg', '.jpeg', '.webp']

def to_snake_case(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return name.lower()

def download_logo(logo_url: str, college_name: str, save_dir: str = 'logos') -> str:
    if not logo_url:
        return ""
    if logo_url.lower().endswith('.svg'):
        pass # Allow SVGs
        
    blacklisted = ['flag', 'emblem', 'netflix', 'microsoft', 'apple', 'google', 'play_store', 'app_store', 'facebook', 'twitter', 'linkedin', 'g20', 'g-20', 'amrit', 'mahotsav', 'azadi', 'reddit', 'byju', 'host', 'besthoster']
    if any(b in logo_url.lower() for b in blacklisted):
        logger.warning(f"Rejected blacklisted URL: {logo_url}")
        return ""
        
    os.makedirs(save_dir, exist_ok=True)
    base_name = to_snake_case(college_name)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(logo_url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        # Check initial extension from URL
        _, ext = os.path.splitext(urllib_parse_path(logo_url))
        ext = ext.lower()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'image/svg' in content_type or ext == '.svg':
            ext = '.svg'
        elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
            ext = '.jpg'
        elif 'image/png' in content_type:
            ext = '.png'
        elif 'image/webp' in content_type:
            ext = '.webp'
            
        if ext in REJECTED_FORMATS:
            logger.warning(f"Rejected format {ext} for {logo_url}")
            return ""
            
        if ext == '.svg':
            # Save SVG natively
            save_path = os.path.join(save_dir, f"{base_name}.svg")
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
            
        # For raster images, use Pillow to verify and possibly convert
        try:
            img = Image.open(BytesIO(response.content))
            
            if img.format == 'GIF' or img.format == 'BMP' or img.format == 'TIFF':
                logger.warning(f"Rejected Pillow format {img.format} for {logo_url}")
                return ""
                
            if img.format == 'WEBP':
                img = img.convert('RGBA')
                ext = '.png'
                save_path = os.path.join(save_dir, f"{base_name}{ext}")
                img.save(save_path, 'PNG')
                return save_path
                
            # If JPG or PNG, save original bytes
            if img.format == 'JPEG':
                ext = '.jpg'
            elif img.format == 'PNG':
                ext = '.png'
                
            save_path = os.path.join(save_dir, f"{base_name}{ext}")
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
            
        except Exception as e:
            logger.warning(f"Pillow failed on {logo_url}: {e}. Trying raw save if format known.")
            if ext in ['.jpg', '.jpeg', '.png']:
                save_path = os.path.join(save_dir, f"{base_name}{ext}")
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return save_path
            return ""
            
    except Exception as e:
        logger.error(f"Download failed for {logo_url}: {e}")
        return ""

def urllib_parse_path(url):
    import urllib.parse
    return urllib.parse.urlparse(url).path
