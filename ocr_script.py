import pytesseract
import cv2
import numpy as np
import os
import re


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 
FOLDER_PATH = r'C:\Users\kala_\OneDrive\Desktop\ocr_test'
LANGUAGES = 'tam+eng'  
OCR_CONFIG = r'--psm 6'  

def preprocess_image(image_path):
    """Loads image, converts to grayscale, and applies adaptive thresholding."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

def extract_invoice_data(text):
    """Tries to find an 8-digit sequence (common invoice number format)."""

    invoice_number_match = re.search(r'\b\d{4}-\d{5}\b', text)
    
    data = {
        "Invoice Number": invoice_number_match.group(0) if invoice_number_match else "Not Found"
    }
    return data


def run_ocr_batch(folder_path):
    print("--- Starting Enhanced OCR Process ---")
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_path = os.path.join(folder_path, filename)
            print(f"\nProcessing {filename}...")
            
    
            processed_img = preprocess_image(image_path)
            if processed_img is None:
                continue

            try:
    
                raw_text = pytesseract.image_to_string(processed_img, lang=LANGUAGES, config=OCR_CONFIG)
                print(" -> OCR Complete.")
                extracted_data = extract_invoice_data(raw_text)
                print("--- RAW EXTRACTED TEXT (for debugging) ---")
                print(raw_text)
                print("------------------------------------------")
                print(f" -> Data Extraction: Invoice Number: {extracted_data['Invoice Number']}")
                
            except Exception as e:
                print(f" -> An unexpected error occurred during OCR for {filename}: {e}")

    print("\n--- OCR Run Complete ---")


if __name__ == '__main__':
    run_ocr_batch(FOLDER_PATH)
