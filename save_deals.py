import json
import pandas as pd

def save_file(all_data, JSON_OUT, EXCEL_OUT, EXCEL_COLUMNS, map_to_excel):
    """
    Saves scraped deal data to JSON and Excel files.

    Parameters:
    - all_data: List of deal dictionaries
    - JSON_OUT: Output JSON file path
    - EXCEL_OUT: Output Excel file path
    - EXCEL_COLUMNS: List of column names for Excel
    - map_to_excel: Function to convert each deal dict to a list for Excel row
    """
    # Save data in JSON format
    with open(JSON_OUT, "w") as f:
        json.dump(all_data, f, indent=4)

    # Save data in Excel format
    pd.DataFrame([map_to_excel(x) for x in all_data], columns=EXCEL_COLUMNS).to_excel(EXCEL_OUT, index=False)
    print("Deals saved to Excel and JSON files.")
