📌 Project Overview

Web Scraper with Gemini is a Python-based tool designed to automate the extraction of contact information from websites. Leveraging Google's Gemini AI for intelligent data extraction,
it reads a list of private equity firms from a Google Sheet and processes their associated URLs to gather relevant contact details.

🧰 Features

Reads firm names and URLs from a Google Sheet
Utilizes Gemini AI for intelligent data extraction
Handles pagination to traverse multiple pages
Saves extracted data in both JSON and Excel formats

🚀 Getting Started

Prerequisites
Python 3.7 or higher
Google API credentials
Gemini API key

Installation
1. Clone the repository:
GitHub
git clone https://github.com/suprithay/web-scraper-with-gemini.git
cd web-scraper-with-gemini
2. Create and activate a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the required dependencies:
pip install -r requirements.txt

4. Set up environment variables:
Create a .env file in the project root directory.
Add your Gemini API key and any other necessary configuration:
GEMINI_API_KEY=your_gemini_api_key

📝 Usage

1. Ensure your Google Sheet is accessible and contains the necessary columns:
    PE Firm
    URL
2. Update the GOOGLE_SHEET_EDIT_URL in config.py with the link to your Google Sheet.
   ✅ Make your Google Sheet public (viewable by link)
    Important: To allow the scraper to access your Google Sheet, make sure your sheet’s sharing settings are set to:
    “Anyone with the link can view”
3. Run the main script:
    python main.py
4. Upon completion, the extracted data will be saved as:
    scraped_results.json
    scraped_results.xlsx

🛠️ Project Structure

.
├── config.py             # Configuration variables
├── contact_scraper.py    # Functions to scrape contact information
├── gemini_extractor.py   # Integrates with Gemini AI for data extraction
├── helper.py             # Utility functions
├── main.py               # Main script to orchestrate the scraping process
├── pagination.py         # Handles pagination logic
├── requirements.txt      # Python dependencies
└── .gitignore            # Specifies files to ignore in version control
