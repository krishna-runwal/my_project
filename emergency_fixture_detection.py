import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np
from difflib import get_close_matches
import re
import os

print("Imported successfully!")

manual_corrections = {
    'SHTIN': 'FITTING',
    'OCHI': 'COACH',
    '1EDUL': 'EDUL',
    '9CHEL': 'CHEL',
    'INGS': 'FITTINGS',
    'TING': 'LIGHTING',
    # OCR corrections for emergency symbols
    'EMI': 'EM',
    'EML': 'EM',
    'A1F': 'A1E',
    'AlE': 'A1E',
    'EXIIT': 'EXIT',
    'FXIT': 'EXIT',
    # Fix common OCR mistakes for "SCHEDULE"
    'JULE': 'SCHEDULE',
    'DULE': 'SCHEDULE', 
    'JEDULE': 'SCHEDULE',
    'HEDULE': 'SCHEDULE',
    'HHEDULI': 'SCHEDULE',
    'CHEDU': 'SCHEDULE',
    'SCHED': 'SCHEDULE',
    'SCHE': 'SCHEDULE',
    # Fix "LIGHTING" mistakes
    'HTING': 'LIGHTING',
    'GHTING': 'LIGHTING',
    'LIGHTIN': 'LIGHTING',
    'LIGH': 'LIGHTING',
    # Other common words
    'UNSWITCHFD': 'UNSWITCHED',
    'SWITCHFD': 'SWITCHED'
}

# Words to IGNORE (table headers and noise)
ignore_words = [
    'SCHEDULE', 'LIGHTING', 'FITTING', 'FITTINGS', 'COACH', 'TABLE', 
    'NTS', 'HIGH', 'DUE', 'WE', 'OE', 'EY', 'ES', 'EE', 'ET', 'CE', 
    'CED', 'DHE', 'GR', 'SK', 'MAR', 'NN', 'YP', 'CI', 'CA', 'ENN', 
    'GAT', 'CT', 'FED', 'IST', 'UST', 'LIGE', 'FT20', 'SOT', 'SS08E', 
    'SONE', 'NG', 'SCH', 'IT20', 'RS', 'FT', 'SC', 'RE', 'RN', 'OIR', 
    'PAIN', 'JULIE', 'JUUE', 'UE', 'DULIE', 'DUDE', 'SOULE', 'HEDUL', 
    'EDU', 'IHEDULE', 'ICHED', 'GHTINC', 'GARIN', 'LEDS'
]

# Valid emergency lighting symbols we want to keep
valid_emergency_symbols = [
    "A1E", "EM", "EXIT", "E", "WL", "WP", "EL", "EX", "SC", "3SC",
    "EMERGENCY", "UNSWITCHED", "SWITCHED", "WALL", "PACK", "LED", "LIGHT"
]

def convert_pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    return [np.array(img) for img in images]

def detect_shaded_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Morph to close small gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter by size (tweak these based on PDF)
        if 20 < w < 150 and 20 < h < 150:
            boxes.append((x, y, x + w, y + h))
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return boxes, image

valid_symbols = [
    "EM", "EXIT", "E", "WL", "WP", "EL", "A1E", "EX", "SC", "3SC", "LIGHT", 
    "LIGH", "CHE", "HE", "UL", "UE", "WC", "WALL", "PANEL", "BATTERY", "FIXTURE"
]

def correct_symbol(raw_symbol):
    cleaned = re.sub(r'^\d+', '', raw_symbol.strip().replace('=', '').replace('–', '-'))
    if cleaned in manual_corrections:
        return manual_corrections[cleaned]
    matches = get_close_matches(cleaned, valid_symbols, n=1, cutoff=0.75)
    return matches[0] if matches else cleaned

def extract_nearby_text(image, box, padding=150):
    """FIXED: Extract MORE text around fixtures"""
    x1, y1, x2, y2 = box
    h, w = image.shape[:2]

    # Calculate padded coordinates - BIGGER area
    x1_pad = max(0, x1 - padding)
    y1_pad = max(0, y1 - padding)
    x2_pad = min(w, x2 + padding)
    y2_pad = min(h, y2 + padding)

    # Extract region of interest
    roi = image[y1_pad:y2_pad, x1_pad:x2_pad]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Try multiple preprocessing methods
    # Method 1: Original with blur
    blurred = cv2.GaussianBlur(gray_roi, (3, 3), 0)
    _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Method 2: Direct threshold with different value
    _, thresh2 = cv2.threshold(gray_roi, 180, 255, cv2.THRESH_BINARY)
    
    # Method 3: Adaptive threshold
    thresh3 = cv2.adaptiveThreshold(gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Save debug images
    os.makedirs("debug", exist_ok=True)
    cv2.imwrite(f"debug/roi_thresh1_{x1}_{y1}.png", thresh1)
    cv2.imwrite(f"debug/roi_thresh2_{x1}_{y1}.png", thresh2)
    cv2.imwrite(f"debug/roi_thresh3_{x1}_{y1}.png", thresh3)

    # OCR all three methods and collect ALL text
    all_text_lines = []
    
    for i, thresh_img in enumerate([thresh1, thresh2, thresh3]):
        # Try different PSM modes
        for psm in [4, 6, 7, 8]:
            try:
                config = f'--psm {psm}'
                text = pytesseract.image_to_string(thresh_img, config=config)
                for line in text.split('\n'):
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 1:
                        all_text_lines.append(clean_line.upper())
            except:
                continue
    
    # Process all captured text into individual words
    all_words = []
    for line in all_text_lines:
        # Clean the line
        cleaned_line = re.sub(r'[^A-Za-z0-9\s]', ' ', line)
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()
        
        # Split into words
        words = cleaned_line.split()
        for word in words:
            if (2 <= len(word) <= 15 and  # Reasonable length
                not word.isdigit() and    # Not just numbers
                word not in all_words):   # Not duplicate
                all_words.append(word)
    
    # Remove duplicates and return up to 6 words
    unique_words = list(dict.fromkeys(all_words))  # Preserves order
    return unique_words[:6] if unique_words else ["Unknown"]

def process_pdf(pdf_path, sheet_name="E2.4"):
    results = []
    images = convert_pdf_to_images(pdf_path)

    for i, img in enumerate(images):
        boxes, annotated = detect_shaded_rectangles(img)
        for box in boxes:
            text_near = extract_nearby_text(img, box)
            
            # Choose the most likely symbol (first text line)
            symbol = text_near[0] if text_near else "Unknown"
            corrected_symbol = correct_symbol(symbol)

            # Clean the symbol a bit (remove stray characters)
            symbol_cleaned = corrected_symbol.strip().replace('=', '').replace('–', '-')

            results.append({
                "symbol": symbol_cleaned,
                "bounding_box": list(box),
                "text_nearby": text_near,
                "source_sheet": f"{sheet_name}"
            })

    return results

if __name__ == "__main__":
    result = process_pdf("PDF.pdf", sheet_name="E2.4")
    for r in result:
        print(r)
    
    # Save to JSON
    import json
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ Output saved to output.json")