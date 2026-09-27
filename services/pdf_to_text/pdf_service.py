from flask import Flask, request, jsonify
import pdfplumber

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_text():
    print("--- Incoming Request: High-Fidelity PDF Extraction ---")
    if 'file' not in request.files:
        return jsonify({"error": "Missing file in request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Load the file stream directly into pdfplumber's layout canvas engine
        with pdfplumber.open(file) as pdf:
            extracted_content = []
            
            for page in pdf.pages:
                # layout=True forces the engine to respect visual positioning and column splits
                text = page.extract_text(layout=True)
                if text:
                    extracted_content.append(text)
            
            complete_text = "\n".join(extracted_content)
            
            # Diagnostic tracking print to see if our target text is captured
            print(f" -> Successfully parsed: '{file.filename}' ({len(pdf.pages)} pages)")
            print(f" -> Total Characters Harvested: {len(complete_text)}")
            
            return jsonify({
                "status": "success",
                "filename": file.filename,
                "page_count": len(pdf.pages),
                "text": complete_text
            }), 200
            
    except Exception as e:
        print(f" ❌ Extraction Engine Fault: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Upgraded PDF Extractor Service running on http://127.0.0.1:5004")
    app.run(port=5004, debug=True)