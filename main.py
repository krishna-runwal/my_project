from flask import Flask, request, jsonify
from checking import process_pdf_to_context 
from final_prompttemplate_code_for_gemmini import get_final_output
import os
import threading
import time
import json
from werkzeug.utils import secure_filename
from final_prompttemplate_code_for_gemmini import get_final_output

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/blueprints/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected."}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(file_path)
            print(f"[INFO] File saved at {file_path}")
            print(f"[DEBUG] File exists: {os.path.exists(file_path)}")

            time.sleep(1)  # Optional: to rule out race condition

            process_pdf_to_context(file_path, output_txt="cleaned_context.txt")

            return jsonify({
                "status": "uploaded",
                "pdf_name": filename,
                "message": "Processing started in background."
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"An error occurred during processing: {str(e)}"
            }), 500
    else:
        return jsonify({"status": "error", "message": "Only PDF files are allowed."}), 400
    

# do the same for the 
RESULT_FOLDER = 'outputs'  # Folder where results are stored
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/blueprints/result', methods=['GET'])
def get_result():
    pdf_name = request.args.get('pdf_name')
    
    if not pdf_name:
        return jsonify({"status": "error", "message": "Missing 'pdf_name' in query parameters."}), 400
    
    # final output
    result_data = get_final_output(pdf_name)
    
    return jsonify({
        "pdf_name": pdf_name,
        "status": "complete",
        "result": result_data
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
