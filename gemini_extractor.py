# gemini_extractor.py

import os
from google import genai
import re
import json
from config import GEMINI_API_KEY

def extract_deals_with_gemini(html_content: str) -> list:
    gemini_api_key = os.getenv('GEMINI_API_KEY')  # Reads from .env file
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file or environment.")

    client = genai.Client(api_key=gemini_api_key)
    prompt = """
        Extract all deals from this page.

        For each deal, return the following fields:
        - title
        - revenue
        - ebitda
        - askingPrice
        - industry
        - dealCaption

        Respond ONLY with a valid JSON object inside a markdown-style code block like this:

        ```json
        {
        "deals": [
            {
            "title": "Deal Title",
            "revenue": "$1,000,000",
            "ebitda": "$200,000",
            "askingPrice": "$500,000",
            "industry": "Industry Name",
            "dealCaption": "Brief caption or summary"
            }
        ]
        }
        """.strip()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"{prompt}\n\n{html_content}"
        )

        # Extract JSON from markdown code block
        match = re.search(r"```json\n(.*?)\n```", response.text, re.DOTALL)
        if match:
            json_data = match.group(1)
            return json.loads(json_data)["deals"]
        else:
            print("No JSON code block found in Gemini response.")
            return []

    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return []