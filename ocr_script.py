import pytesseract
from PIL import Image
import os
import re
import cv2 
import numpy as np

# --- CONFIGURATION (Customize these settings) ---

# 1. SET THE FOLDER PATH
# IMPORTANT: This path must be correct!
folder_path = r"C:\Users\kala_\OneDrive\Desktop\ocr_test" 

# 2. SET THE LANGUAGE CODE (Use 'eng' for English, or 'eng+tam' for English and Tamil)
ocr_language = 'eng' 

# 3. DEFINE IMAGE EXTENSIONS TO PROCESS
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff') 

# 4. SET THE REGULAR EXPRESSION (RegEx) PATTERN
# **UPDATE THIS PATTERN** after reviewing the raw text output!
# Example below looks for "Invoice No" or "INV" followed by mixed alphanumeric characters/slashes
invoice_pattern = r"(Invoice No|INV|Ref)[:\s]*([\w/]+)"

# -------------------------------------------------

def preprocess_image(image_path):
    """Cleans the image using OpenCV for better OCR results."""
    # Read the image using OpenCV
    img = cv2.imread(image_path)
    
    # Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian Blur (optional, helps with noise reduction)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Adaptive Thresholding (converts to pure black/white)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Convert the OpenCV object back to a PIL Image object for Tesseract
    return Image.fromarray(thresh)


# --- START MAIN EXECUTION ---
print("--- Starting Advanced Batch OCR Process ---")
print(f"Targeting folder: {folder_path}")
print(f"Using Tesseract Language: {ocr_language}")

# Loop through all files in the specified folder
for filename in os.listdir(folder_path):
    # Check if the file is an image
    if filename.lower().endswith(IMAGE_EXTENSIONS):
        
        input_path = os.path.join(folder_path, filename)
        
        # Naming the Output File
        base_name = os.path.splitext(filename)[0]
        output_pdf_filename = base_name + "_searchable.pdf" 
        output_pdf_path = os.path.join(folder_path, output_pdf_filename)
        
        print(f"\nProcessing {filename}...")
        
        try:
            # 1. Image Pre-processing
            img = preprocess_image(input_path) 
            
            # --- PHASE 1: OCR AND PDF CREATION ---
            
            # Create the searchable PDF bytes
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                img, 
                lang=ocr_language, 
                extension='pdf' 
            )
            
            # Save the PDF file
            with open(output_pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"  -> SUCCESS! Searchable PDF saved to {output_pdf_filename}")

            # --- PHASE 2: DATA EXTRACTION ---
            
            # Get the raw text string for parsing
            raw_text = pytesseract.image_to_string(img, lang=ocr_language)
            
            # **DEBUGGING LINE: SEE THE RAW TEXT TO FIX YOUR REGEX**
            print("\n--- RAW EXTRACTED TEXT (for debugging) ---")
            print(raw_text)
            print("------------------------------------------\n")

            # Perform Data Extraction
            match = re.search(invoice_pattern, raw_text, re.IGNORECASE)
            
            if match:
                # Group 2 is the actual captured number from the RegEx pattern
                invoice_number = match.group(2).strip()
                print(f"  -> FOUND Invoice Number: {invoice_number}")
                
                # Further logic: save 'invoice_number' to a database or CSV here.
            else:
                print("  -> Data Extraction: Invoice Number not found (RegEx did not match).")

        except pytesseract.TesseractNotFoundError:
            print("  -> FATAL ERROR: Tesseract is not found. Check Tesseract installation and PATH.")
        except Exception as e:
            print(f"  -> ERROR processing {filename}: {e}")
            
print("\n--- Batch OCR Complete ---")