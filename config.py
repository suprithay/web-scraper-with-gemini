# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_EDIT_URL = (
    "https://docs.google.com/spreadsheets/"
    "d/1PBnfjxAqdKdU-XBP6Mh4AhEkOzN332HF6mU2zNbM2gM/export?format=csv"
)

FIRM_COL, URL_COL = "PE Firm", "URL"
JSON_OUT = "scraped_results.json"
EXCEL_OUT = "scraped_results.xlsx"
scraped_urls = set()

PROMPT = """
Extract all deals from this page.
For each deal, return:
- title
- Revenue
- ebitda
- askingPrice
- industry
- dealCaption
Return as "deals"
""".strip()

EXCEL_COLUMNS = [
    "Brokerage", "First Name", "Last Name", "Work Phone", "Email", "LinkedIn URL",
    "Deal Caption", "Revenue", "EBITDA", "EBITDA Margin", "Industry",
    "Source Website", "Upload", "UploadOnCRM", "Company Location"
]

COLUMN_MAPPING = {
    "brokerage": "Brokerage",
    "firstName": "First Name",
    "lastName": "Last Name",
    "workPhone": "Work Phone",
    "email": "Email",
    "linkedinUrl": "LinkedIn URL",
    "dealCaption": "Deal Caption",
    "revenue": "Revenue",
    "ebitda": "EBITDA",
    "ebitdaMargin": "EBITDA Margin",
    "industry": "Industry",
    "sourceWebsite": "Source Website",
    "companyLocation": "Company Location"
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
