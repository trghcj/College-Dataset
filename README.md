# College Logo Dataset Scraper

This repository contains a Python-based, multi-tiered web scraping pipeline designed to gather official, high-quality logos for engineering colleges in India. It accepts a CSV file containing a list of colleges and produces an enriched CSV dataset alongside a curated directory of validated logo images.

## Architecture & Flowchart

The scraper operates through an extensive 10-Tier fallback system to maximize accuracy and minimize placeholder/incorrect logos. It strictly prioritizes educational domains (`.ac.in`, `.edu.in`) and uses location-based filtering to prevent domain collisions (e.g. two colleges in the same city grabbing each other's website).

```mermaid
flowchart TD
    Start[Input: College Name] --> Tier0{Tier 0: Local Cache}
    Tier0 -- Found --> Validate[Validation Check]
    Tier0 -- Missing --> Tier1{Tier 1: Wikidata P154}
    Tier1 -- Found --> Validate
    Tier1 -- Missing --> Tier2{Tier 2: Wikipedia Infobox}
    Tier2 -- Found --> Validate
    Tier2 -- Missing --> FindDomain[DuckDuckGo: Find Official Website]
    FindDomain --> Tier3{Tier 3: Website Favicon}
    Tier3 -- Found --> Validate
    Tier3 -- Missing --> Tier4{Tier 4: OpenGraph Tags}
    Tier4 -- Found --> Validate
    Tier4 -- Missing --> Tier5{Tier 5: JSON-LD Schema}
    Tier5 -- Found --> Validate
    Tier5 -- Missing --> Tier6{Tier 6: Header / CSS Background}
    Tier6 -- Found --> Validate
    Tier6 -- Missing --> Tier7{Tier 7: Common Paths}
    Tier7 -- Found --> Validate
    Tier7 -- Missing --> Tier8{Tier 8: GitHub Search}
    Tier8 -- Found --> Validate
    Tier8 -- Missing --> Tier9{Tier 9: Filetype Search}
    Tier9 -- Found --> Validate
    Tier9 -- Missing --> Tier10{Tier 10: DDG Image Search}
    Tier10 -- Found --> Validate
    Tier10 -- Missing --> Fail[Log to failed.csv]
    
    Validate -- Transparent PNG/SVG --> HashCheck{Hash Check}
    Validate -- Bad Size/Ratio/Background --> Fail
    
    HashCheck -- Generic Placeholder Hash --> Fail
    HashCheck -- Unique Hash --> Success[Save Logo & Add to CSV]
```

## Advanced Features

1. **SVG Thumbnail Rendering**: Automatically bypasses standard SVG download rejections by hooking into the Wikipedia API to fetch pre-rendered `500px` PNG thumbnails for vector graphics.
2. **Cryptographic Placeholder Filtering**: Computes in-memory MD5 hashes of all downloaded images and instantly rejects standard generic placeholders (like Wikipedia's \"image needed\" book or DDG's default icons).
3. **Location-Aware Deduplication**: Extracts the City/State of the college and validates scraped websites to prevent cross-matching colleges that share acronyms in the same region.
4. **Transparency Enforcer**: Rejects any raster image (JPG/PNG) that lacks at least one transparent pixel, ensuring no ugly white-box backgrounds make it into the final dataset.

## Setup

```bash
pip install -r requirements.txt
python build_dataset.py
```
