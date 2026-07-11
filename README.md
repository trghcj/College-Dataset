# College Logo Dataset Scraper

This repository contains a Python-based, multi-tiered web scraping pipeline designed to gather official, high-quality logos for engineering colleges in India. It accepts a CSV file containing a list of colleges and produces an enriched CSV dataset alongside a curated directory of validated logo images.

## Project Structure

- `build_dataset.py`: The main entry point script. Reads `colleges.csv`, coordinates the scraping process concurrently, and produces `engineering_colleges.csv` and `failed.csv`.
- `scraper/`: A module containing specialized scraping logic:
  - `commons_downloader.py`: Downloads images from Wikimedia Commons.
  - `html_extractor.py`: Parses HTML to find logos in favicons, OpenGraph tags, JSON-LD structured data, and CSS backgrounds.
  - `image_validator.py`: Validates downloaded images (checking format, transparency, and size constraints).
  - `logo_downloader.py`: Handles fetching images from URLs with a blacklist filter.
  - `logo_resolver.py`: Resolves the best logo from a Wikipedia page (e.g. infoboxes).
  - `path_checker.py`: Checks common default paths (like `/logo.png`) on official websites.
  - `unilogo_search.py`: Searches a local cache of verified university logos.
  - `website_search.py`: Uses DuckDuckGo to discover the official website for a college name, applying strict educational domain prioritization (`.ac.in`, `.edu.in`, etc.).
  - `wiki_client.py`: Wikipedia API utility methods.
  - `wiki_search.py`: Resolves college names to Wikipedia titles and Wikidata IDs.
  - `wikidata_logo.py`: Fetches the official logo entity (P154) from Wikidata.
- `logos/`: Output directory where downloaded logos are saved.
- `colleges.csv`: The input list of colleges.
- `engineering_colleges.csv`: The final successfully enriched output dataset.
- `failed.csv`: Output list of colleges that failed all tiers or did not produce a validated logo.

## How It Works

The scraper operates in multiple "Tiers", falling back to less reliable sources only if earlier tiers fail to produce a valid transparent logo:
1. **Tier 0:** Local Repository cache (e.g., UniLogo dataset).
2. **Tier 1:** Wikidata Entity (P154).
3. **Tier 2:** Wikipedia Infobox / Page Image.
4. **Tier 3:** Official Website Favicon.
5. **Tier 4:** Official Website OpenGraph Tags.
6. **Tier 5:** Official Website JSON-LD Structured Data.
7. **Tier 6:** Official Website Header/CSS Background Logo.
8. **Tier 7:** Common Paths (e.g., `/images/logo.png`).
9. **Tier 8 & 9:** Direct Search Engine Queries (DuckDuckGo / GitHub).

### Image Validation
Downloaded images go through a rigorous validation check. Valid logos must:
- Have a minimum size (e.g., > 75x75 px).
- Have a reasonable aspect ratio.
- (For PNG/WebP) Have at least one transparent pixel to avoid generic boxy background photos.

## Setup

```bash
pip install -r requirements.txt
python build_dataset.py
```
