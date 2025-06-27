# helper.py

import re
import hashlib
from config import COLUMN_MAPPING
import undetected_chromedriver as uc

def parse_money(value):
    if not value or not isinstance(value, str):
        return None
    value = value.strip().replace("$", "").replace(",", "").upper()

    multiplier = 1
    if value.endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith("B"):
        multiplier = 1_000_000_000
        value = value[:-1]
    elif value.endswith("K"):
        multiplier = 1_000
        value = value[:-1]

    try:
        return float(value.strip()) * multiplier
    except ValueError:
        return None

def create_undetected_driver(headless=False):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # Use the new headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    return driver

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def sheet_to_csv_url(edit_url: str) -> str:
    m = re.match(r".*/d/([a-zA-Z0-9-_]+)", edit_url)
    if not m:
        raise ValueError("Invalid Google Sheet URL")
    return f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"

def hash_content(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def map_to_excel(item):
    return {COLUMN_MAPPING[k]: v for k, v in item.items() if k in COLUMN_MAPPING}

def add_unique_deals(deals: list, seen_keys: set) -> list:
        new_deals = []
        for deal in deals:
            key = (deal.get("title"), deal.get("dealCaption"))
            if key not in seen_keys:
                if any(bad_word in (deal.get("dealCaption") or "").lower()
                       for bad_word in ["sold", "inactive", "off market", "not available"]):
                    continue
                seen_keys.add(key)
                new_deals.append(deal)
        return new_deals