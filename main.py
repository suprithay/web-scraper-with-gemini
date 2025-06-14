# main.py

import pandas as pd
import os
import json
from datetime import datetime
from contact_scraper import scrape_contacts_with_selenium
from pagination import scrape_all_deals_with_pagination
from helper import sheet_to_csv_url
from helper import parse_money
from config import (JSON_OUT, GOOGLE_SHEET_EDIT_URL, FIRM_COL, URL_COL, EXCEL_COLUMNS, EXCEL_OUT)
from helper import map_to_excel
from save_deals import save_file

def main():
    # Load existing data if it exists
    if os.path.exists(JSON_OUT):
        with open(JSON_OUT, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Track (firm, dealCaption) pairs to avoid duplicates
    existing_keys = {
        (d["brokerage"], d["dealCaption"]) for d in existing_data
    }

    df = pd.read_csv(sheet_to_csv_url(GOOGLE_SHEET_EDIT_URL))
    all_data = existing_data.copy()

    for index, row in df.iterrows():
        firm_name = str(row.get(FIRM_COL)).strip()
        url = str(row.get(URL_COL)).strip()
        
        # Skip if any deal from this firm already exists
        if any(firm_name == d["brokerage"] for d in existing_data):
            print(f"Skipping already scraped: {firm_name}")
            continue
        
        print(f"Scraping {firm_name} - {url}")

        try:
            contact_info = scrape_contacts_with_selenium(url, firm_name)
            deals = scrape_all_deals_with_pagination(url)

            if not deals:
                print(f"No deals found for {firm_name}")
                continue

            for deal in deals:
                deal_caption = deal.get("dealCaption") or deal.get("title", "Not Found")
                key = (firm_name, deal_caption)
                if key in existing_keys:
                    continue

               # Clean and parse numbers using parse_money
                revenue = parse_money(deal.get("revenue"))
                ebitda = parse_money(deal.get("ebitda"))
                asking_price = parse_money(deal.get("askingPrice"))
                #ebitdaMargin = round(ebitda / revenue, 2) if ebitda and revenue else None
                ebitdaMargin = round((ebitda / revenue) * 100, 2) if ebitda and revenue else None

                gross_revenue = revenue  # assuming same as revenue for now

                # Prepare and append data to Excel & JSON
                data = {
                    "id": "",  
                    "brokerage": firm_name,
                    "firstName": contact_info.get("First Name") if contact_info else None,
                    "lastName": contact_info.get("Last Name") if contact_info else None,
                    "email": contact_info.get("Email") if contact_info else None,
                    "linkedinUrl": contact_info.get("LinkedIn URL") if contact_info else None,
                    "workPhone": contact_info.get("Work Phone") if contact_info else None,
                    "dealCaption": deal_caption,
                    "revenue": revenue,
                    "ebitda": ebitda,
                    "title": deal.get("title") or None,
                    "grossRevenue": gross_revenue,
                    "askingPrice": asking_price,
                    "ebitdaMargin": ebitdaMargin,
                    "industry": deal.get("industry") or "Not Found",
                    "dealType": "MANUAL",
                    "sourceWebsite": url,
                    "companyLocation": contact_info.get("Company Location") if contact_info else None,
                    "createdAt": datetime.utcnow().isoformat() + "Z",
                    "updatedAt": datetime.utcnow().isoformat() + "Z",
                    "bitrixId": None,
                    "bitrixCreatedAt": None,
                    "SIM": [],
                    "AiScreening": []
                }

                all_data.append(data)
                existing_keys.add(key)

            save_file(all_data, JSON_OUT, EXCEL_OUT, EXCEL_COLUMNS, map_to_excel)
            print("Deals saved to excel sheet")
        except Exception as e:
            print(f"Error scraping {firm_name}: {e}")
             # 🔥 Save what has been collected so far before crashing
            save_file(all_data, JSON_OUT, EXCEL_OUT, EXCEL_COLUMNS, map_to_excel)
            print(f"Emergency save done after crash on {firm_name}")

if __name__ == "__main__":
    main()