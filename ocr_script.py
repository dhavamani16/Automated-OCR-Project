import pytesseract
import cv2
import numpy as np
import os
import re

# 1. SET THE TESSERACT PATH - YOUR CONFIRMED PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 

# 2. CONFIGURATION
# Set the folder where your script and images are located
FOLDER_PATH = r'C:\Users\kala_\OneDrive\Desktop\ocr_test'
LANGUAGES = 'tam+eng'  # Use both Tamil (tam) and English (eng) models
OCR_CONFIG = r'--psm 6'  # PSM 6: Assumes a single uniform block of text (good for forms)

# 3. PREPROCESSING FUNCTION 🛠️
def preprocess_image(image_path):
    """Loads image, converts to grayscale, and applies adaptive thresholding."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Adaptive Thresholding creates a clean black-and-white image, essential for OCR
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

# 4. DATA EXTRACTION FUNCTION
def extract_invoice_data(text):
    """Tries to find an 8-digit sequence (common invoice number format)."""
    # Look for a sequence of 8 to 12 digits, surrounded by word boundaries (\b)
    invoice_number_match = re.search(r'\b\d{4}-\d{5}\b', text)
    
    data = {
        "Invoice Number": invoice_number_match.group(0) if invoice_number_match else "Not Found"
    }
    return data

# 5. MAIN PROCESSING LOGIC
def run_ocr_batch(folder_path):
    print("--- Starting Enhanced OCR Process ---")
    
    # Iterate through all files in your designated folder
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            print(f"\nProcessing {filename}...")
            
            # Preprocess the image
            processed_img = preprocess_image(image_path)
            if processed_img is None:
                continue

            try:
                # Perform OCR using the preprocessed image, multi-language, and PSM config
                raw_text = pytesseract.image_to_string(processed_img, lang=LANGUAGES, config=OCR_CONFIG)
                print(" -> OCR Complete.")

                # Extract Structured Data
                extracted_data = extract_invoice_data(raw_text)

                # Print Results
                print("--- RAW EXTRACTED TEXT (for debugging) ---")
                print(raw_text)
                print("------------------------------------------")
                print(f" -> Data Extraction: Invoice Number: {extracted_data['Invoice Number']}")
                
            except Exception as e:
                print(f" -> An unexpected error occurred during OCR for {filename}: {e}")

    print("\n--- OCR Run Complete ---")


if __name__ == '__main__':
    run_ocr_batch(FOLDER_PATH)