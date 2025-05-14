# contact_scraper.py

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse
def scrape_contacts_with_selenium(url: str, firm_name: str) -> dict:
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(url)
    time.sleep(3)

    ci = {
        "First Name": "Not Found",
        "Last Name": "Not Found",
        "Email": "Not Found",
        "LinkedIn URL": "Not Found",
        "Work Phone": "Not Found",
        "Brokerage": firm_name,
        "Company Location": "Not Found"
    }

    def extract(soup, text):
        if ci["Email"] == "Not Found":
            m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
            if m: ci["Email"] = m.group(0)

        if ci["Work Phone"] == "Not Found":
            m = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
            if m: ci["Work Phone"] = m.group(0)

        if ci["LinkedIn URL"] == "Not Found":
            for a in soup.find_all("a", href=True):
                if "linkedin.com" in a["href"]:
                    ci["LinkedIn URL"] = a["href"]
                    break

        if ci["Company Location"] == "Not Found":
            patterns = [
                r"\d{1,5}\s+\w+(?:\s+\w+)*,\s*\w+(?:\s+\w+)*,\s*[A-Z]{2}\s+\d{5}",
                r"\w+(?:\s+\w+)*,\s*[A-Z]{2}\s+\d{5}",
                r"\d{5}(?:-\d{4})?"
            ]
            for section in ['header', 'footer']:
                sec = soup.find(section)
                if sec:
                    section_text = sec.get_text(" ", strip=True)
                    for pat in patterns:
                        m = re.search(pat, section_text)
                        if m:
                            ci["Company Location"] = m.group(0)
                            return
            for pat in patterns:
                m = re.search(pat, text)
                if m:
                    ci["Company Location"] = m.group(0)
                    break

        if ci["First Name"] == "Not Found":
            for tag in soup.find_all(["h1", "h2", "h3", "p"]):
                words = tag.get_text(strip=True).split()
                if len(words) == 2:
                    ci["First Name"], ci["Last Name"] = words
                    return

    soup = BeautifulSoup(driver.page_source, "html.parser")
    extract(soup, driver.find_element(By.TAG_NAME, "body").text)

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(k in href for k in ["contact", "team", "about", "staff", "leadership"]):
            full = href if href.startswith("http") else urlparse(url)._replace(path=href).geturl()
            try:
                driver.get(full)
                time.sleep(2)
                sub = BeautifulSoup(driver.page_source, "html.parser")
                extract(sub, driver.find_element(By.TAG_NAME, "body").text)
                if ci["First Name"] == "Not Found" and ci["Email"] != "Not Found":
                    local = ci["Email"].split("@")[0]
                    parts = re.split(r"[._\-]", local)
                    ci["First Name"] = parts[0].capitalize()
                    if len(parts) > 1:
                        ci["Last Name"] = parts[1].capitalize()
            except Exception as e:
                print(f"Error while scraping contact page {full}: {e}")
                continue

    driver.quit()
    return ci