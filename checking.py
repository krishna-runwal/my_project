import cv2
import pytesseract
import numpy as np
from pdf2image import convert_from_path
import os

# Optional: Set Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def convert_pdf_to_images(pdf_path, dpi=300):
    return [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in convert_from_path(pdf_path, dpi=dpi)]

def extract_text_from_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Optional: improve OCR results
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    text = pytesseract.image_to_string(thresh, config='--psm 6')
    return text.strip()

def process_pdf_to_context(pdf_path, output_txt="cleaned_context.txt"):
    print(f"🔍 Reading PDF: {pdf_path}")
    images = convert_pdf_to_images(pdf_path)
    all_text = []

    for i, img in enumerate(images):
        print(f"📄 Processing Page {i + 1}")
        text = extract_text_from_image(img)
        all_text.append(f"\n### Page {i + 1} ###\n{text}")

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))

    print(f"✅ Full context extracted to '{output_txt}'")

# Run the process
# if __name__ == "__main__":
#     process_pdf_to_context("PDF.pdf", output_txt="cleaned_context.txt")
