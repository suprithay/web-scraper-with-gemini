import os
import re
import time
import json
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from playwright.sync_api import sync_playwright

# === File paths ===
INPUT_EXCEL = "AmericanHealthcare_deals.xlsx" # input xlsx file from the deal scraper
INPUT_JSON = "AmericanHealthcare_deals.json"  # input json file from the deal scraper
OUTPUT_EXCEL = "AmericanHealthcare_url_updater.xlsx"
OUTPUT_JSON = "AmericanHealthcare_url_updater.json"
DELAY_BETWEEN_CALLS = 10  # seconds

def fetch_html_playwright(url: str) -> tuple:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"\n🌐 Visiting {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"❌ Failed to load {url}: {e}")
        return ""

def find_closest_link(deal_caption: str, html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    link_candidates = []

    # Step 1: Match deal caption directly in links
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        href = link['href']
        score = fuzz.partial_ratio(deal_caption.lower(), f"{text} {href}".lower())
        if score >= 60:
            link_candidates.append((score, href))

    if link_candidates:
        link_candidates.sort(reverse=True)
        return urljoin(base_url, link_candidates[0][1])

    # Step 2: Look near matched text (e.g., "Customer base: Res/Com") for teaser-like links
    keywords = ['teaser', 'more info', 'view', 'details', 'learn']

    for node in soup.find_all(string=True):
        if fuzz.partial_ratio(deal_caption.lower(), node.strip().lower()) >= 70:
            parent = node.find_parent()
            if not parent:
                continue

            # Check links in the same container
            for a in parent.find_all('a', href=True):
                if any(k in a.get_text(strip=True).lower() for k in keywords):
                    return urljoin(base_url, a['href'])

            # Check links in sibling containers
            for sibling in parent.find_next_siblings():
                if sibling.name:
                    for a in sibling.find_all('a', href=True):
                        if any(k in a.get_text(strip=True).lower() for k in keywords):
                            return urljoin(base_url, a['href'])

    return ""

def extract_text_with_bs4(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text

def update_deals():
    df = pd.read_excel(INPUT_EXCEL)
    with open(INPUT_JSON, 'r') as f:
        json_data = json.load(f)

    for idx, row in df.iterrows():
        dealCaption = str(row["Deal Caption"]).strip()
        source_url = str(row["Source Website"]).strip()

        print(f"\n🔍 [{idx + 1}] Processing: {dealCaption}")
        listing_html = fetch_html_playwright(source_url)
        if not listing_html:
            print("⚠️ Skipping due to HTML fetch failure.")
            continue

        matched_url = find_closest_link(dealCaption, listing_html, source_url)
        if not matched_url:
            print("⚠️ Skipping: No matching link found.")
            continue

        deal_html = fetch_html_playwright(matched_url)
        if not deal_html:
            print("⚠️ Skipping: Deal page could not be loaded.")
            continue

        description = extract_text_with_bs4(deal_html)
        clean_description = description.replace('\n', ' ').replace('\r', ' ')

        updated_caption = f"{dealCaption} — {clean_description}"
        df.at[idx, "Deal Caption"] = updated_caption
        df.at[idx, "Source Website"] = matched_url

        for deal in json_data:
            original_caption = deal.get("dealCaption", "").strip()

            if original_caption in dealCaption or dealCaption in original_caption:
                # Append the full description, preserving original
                full_caption = f"{original_caption} — {clean_description}"

                deal["dealCaption"] = full_caption
                deal["sourceWebsite"] = matched_url
                break

        print(f"✅ Updated URL: {matched_url}")
        print(f"📝 page_description is updated")
        print(f"⏳ Sleeping {DELAY_BETWEEN_CALLS}s")
        time.sleep(DELAY_BETWEEN_CALLS)

        df.to_excel(OUTPUT_EXCEL, index=False)
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(json_data, f, indent=2)

    print("\n✅ All updates completed.")

if __name__ == "__main__":
    update_deals()
