# pagination.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper import create_undetected_driver
from helper import hash_content
from config import scraped_urls
from gemini_extractor import extract_deals_with_gemini

def scrape_all_deals_with_pagination(start_url: str) -> list:
    if start_url in scraped_urls:
        print(f"🔁 Already scraped: {start_url}, skipping.")
        return []

    scraped_urls.add(start_url)
    driver = create_undetected_driver()
    driver.get(start_url)
    time.sleep(3)

    all_deals = []
    page_num = 1
    seen_deal_keys = set()
    seen_hashes = set()
    prev_url = driver.current_url
    wait = WebDriverWait(driver, 10)

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

    try:
        # === Step 0: Handle Carousel with Arrow ===
        try:
            print("🎠 Attempting to extract from carousel...")
            seen_titles = set()
            carousel_clicks = 0
            max_carousel_clicks = 50
            loop_detected = False

            def extract_carousel_cards():
                cards = driver.find_elements(By.CSS_SELECTOR, "div[data-cy='listing-card']")
                deals = []
                for card in cards:
                    try:
                        title = card.find_element(By.CSS_SELECTOR, "h4").text.strip()
                        caption = card.find_element(By.CSS_SELECTOR, "p").text.strip()
                        if title not in seen_titles:
                            seen_titles.add(title)
                            deals.append({
                                "title": title,
                                "dealCaption": caption,
                            })
                    except:
                        continue
                return deals

            carousel_deals = extract_carousel_cards()
            new_carousel = add_unique_deals(carousel_deals, seen_deal_keys)
            all_deals.extend(new_carousel)

            while carousel_clicks < max_carousel_clicks and not loop_detected:
                try:
                    next_arrow = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next Slide']")))
                    next_arrow.click()
                    time.sleep(2)

                    new_carousel_deals = extract_carousel_cards()
                    new_deals = add_unique_deals(new_carousel_deals, seen_deal_keys)
                    if not new_deals:
                        print("♻️ Carousel loop detected — stopping.")
                        loop_detected = True
                    all_deals.extend(new_deals)
                    carousel_clicks += 1
                except:
                    print("❌ Couldn't click carousel arrow — stopping carousel scraping.")
                    break

            print(f"✅ Carousel scraping complete. Found {len(all_deals)} total deals so far.")
        except Exception as e:
            print(f"⚠️ Carousel scraping failed: {e}")

        # === Step 1: Pagination scraping ===
        while True:
            print(f"🌀 Scraping page {page_num}...")
            time.sleep(2)

            html = driver.page_source
            html_hash = hash_content(html)
            if html_hash in seen_hashes:
                print("⚠️ Duplicate content detected — stopping.")
                break
            seen_hashes.add(html_hash)

            deals = extract_deals_with_gemini(html)
            new_deals = add_unique_deals(deals, seen_deal_keys)

            if not new_deals:
                print("❌ No new deals found — might be finished.")
                break

            print(f"✅ Found {len(new_deals)} new deals on page {page_num}.")
            all_deals.extend(new_deals)

            # === Try "Load More" ===
            try:
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//a[(contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load') or " +
                        "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more') or " +
                        "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show')) and " +
                        "(@href='#' or @role='button')]"
                    ))
                )
                print("🔄 'Load More' found — clicking...")
                driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(1)
                load_more_button.click()
                time.sleep(3)
                page_num += 1
                continue
            except:
                print("❌ No 'Load More' found or clickable.")

            # === Try infinite scroll ===
            scroll_height_before = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_height_after = driver.execute_script("return document.body.scrollHeight")
            if scroll_height_before != scroll_height_after:
                print("🔄 Scrolled and page grew — new content loaded.")
                page_num += 1
                continue
            else:
                print("❌ Scrolling didn’t load more content.")

            # === Try numbered pagination ===
            try:
                next_page_xpath = f"//a[normalize-space(text())='{page_num + 1}']"
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, next_page_xpath))
                )
                print(f"➡️ Clicking numbered page {page_num + 1}")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                next_button.click()
                time.sleep(3)

                current_url = driver.current_url
                if current_url == prev_url:
                    print("⚠️ URL did not change — possibly looping.")
                    break
                prev_url = current_url
                page_num += 1
                continue
            except:
                print("❌ No numbered pagination found.")

            # === Try "Next" or "›" pagination ===
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//a[contains(text(), 'Next') or contains(text(), '›') or contains(text(), '→') or contains(text(), 'Last') or contains(text(), '>>')]"
                    ))
                )
                print("➡️ Clicking 'Next' style pagination...")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                next_button.click()
                time.sleep(3)

                current_url = driver.current_url
                if current_url == prev_url:
                    print("⚠️ URL did not change — possibly last page.")
                    break
                prev_url = current_url
                page_num += 1
                continue
            except:
                print("❌ No 'Next' style pagination found.")

            print("✅ All pagination strategies exhausted.")
            break

    finally:
        driver.quit()
        print("🚪 Driver closed. Returning all deals.")

    return all_deals