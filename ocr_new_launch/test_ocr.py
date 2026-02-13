import pytesseract
import cv2
import numpy as np

print("="*60)
print("TESSERACT TEST")
print("="*60)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print("\nTest 1: Checking Tesseract...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"SUCCESS: Tesseract {version} found")
except Exception as e:
    print(f"ERROR: {e}")
    exit()

print("\nTest 2: Testing OCR...")
try:
  
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'HELLO WORLD', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    cv2.imwrite('test_image.png', img)
    print("Test image created")
 
    text = pytesseract.image_to_string(img)
    print(f"Extracted: {text.strip()}")
    
    if 'HELLO' in text.upper():
        print("SUCCESS: OCR working!")
    else:
        print("WARNING: OCR may not be accurate")
        
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
