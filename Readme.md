# PDF Processing API with OCR + Tesseract + OpenCV + Gemmini LLM

This Flask-based API allows users to upload PDF files, automatically triggers background processing using OCR and AI models, and lets users retrieve the processed structured output.

---

## 📌 What This Project Does

1. Accepts a PDF file upload using Flask.
2. Processes the PDF using:
   - OpenCV for visual parsing (like detecting tables, blocks, etc.)
   - Tesseract OCR for extracting raw text from the PDF
   - A custom prompt system powered by **Gemmini LLM API** for final reasoning & response
3. Saves results in a structured format
4. Lets users retrieve results via a GET API

---

## ⚙️ Technologies Used

- **Flask** for creating the API
- **OpenCV** for image-based document analysis
- **Tesseract OCR** for extracting text
- **Gemmini LLM API** for language model-driven output
- **Python threading** to process files without blocking the API

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/krishna-runwal/pdf-processing-api.git
cd pdf-processing-api


pip install flask opencv-python pytesseract
