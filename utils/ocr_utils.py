import pytesseract #  It reads text from images using Optical Character Recognition (OCR).
from PIL import Image # Opens the image file so that it can be passed to pytesseract for OCR.
import re # Extracts specific structured data (test name, result, reference range, unit) from the OCR’d text.
import pandas as pd # Converts the extracted test results into a structured DataFrame (table format), making it easier to view or export.

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Get Image from User
def perform_ocr(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# --- Test Results Structuring Functions ---
def parse_test_results(text):
    test_pattern = r'([A-Za-z\s]+(?:[A-Za-z]+)?)\s+(\d+(\.\d+)?)\s+([0-9\-]+(?:\.\d+)?(?:\s?-\s?[0-9\-]+(?:\.\d+)?))\s+([A-Za-z/%]+)'
    matches = re.findall(test_pattern, text)

    results = []
    for match in matches:
        test_name = match[0].strip()
        result_value = match[1].strip()
        reference_range = match[3].strip()
        unit = match[4].strip()
        category = categorize_result(result_value, reference_range)

        results.append({
            'Test Name': test_name,
            'Result': result_value,
            'Reference Range': reference_range,
            'Unit': unit,
            'Category': category
        })

    return pd.DataFrame(results)

def categorize_result(result_value, reference_range):
    try:
        result_value = float(result_value)
        min_range, max_range = map(float, reference_range.replace(' ', '').split('-'))
        if result_value < min_range:
            return 'Low'
        elif result_value > max_range:
            return 'High'
        else:
            return 'Normal'
    except:
        return 'Unknown'

# --- Main Execution ---
if __name__ == "__main__":
    image_path = input("Enter the path to the lab report image: ").strip()

    # Load and Optical Character Recognition. image
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    print("\nExtracted OCR Text:\n", text)

    # Parse and structure data
    structured_data = parse_test_results(text)

    print("\nStructured Test Results:")
    print(structured_data)
