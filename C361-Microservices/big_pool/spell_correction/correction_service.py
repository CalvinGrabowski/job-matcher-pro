import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def clean_layout_gaps(text):
    if not text:
        return ""

    # Rule 1: Fix broken single-letter headings (e.g., "F rameworks" -> "Frameworks")
    # Catches a standalone capital letter followed by a space and lowercase letters
    word_split_pattern = re.compile(r'\b([A-Z])\s+([a-z]\w+)\b')
    healed_text = word_split_pattern.sub(lambda m: m.group(1) + m.group(2), text)
    
    # Rule 2: Fix ANY capital letters separated by a space (e.g., "GP A" -> "GPA", "A WS" -> "AWS", "G P A" -> "GPA")
    # Lookahead assertion ensures we match a capital letter, a space, and another capital letter
    acronym_split_pattern = re.compile(r'\b([A-Z]+)\\s+([A-Z]+\\b)')
    
    # Run a loop to completely catch nested multi-space gaps like G P A
    old_text = ""
    while old_text != healed_text:
        old_text = healed_text
        healed_text = acronym_split_pattern.sub(lambda m: m.group(1) + m.group(2), healed_text)
    
    # Rule 3: Fix cases where trailing words are glued directly to split words due to PDF extraction compression
    # Example: "I/Onatively" -> "I/O natively", "I/Oredirection" -> "I/O redirection"
    healed_text = re.sub(r'\bI/O([a-zA-Z]+)', r'I/O \1', healed_text)
    
    # Rule 4: Fix inverse cases where "I/O" is glued to the end of a word
    # Example: "imageI/O" -> "image I/O"
    healed_text = re.sub(r'([a-zA-Z]+)I/O\b', r'\1 I/O', healed_text)

    return healed_text

@app.route('/process', methods=['POST'])
def correct_spelling():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' key in request body"}), 400
        
    raw_text = data['text']
    corrected_output = clean_layout_gaps(raw_text)
            
    return jsonify({
        "original_text": raw_text,
        "corrected_text": corrected_output
    })

if __name__ == '__main__':
    print("Pure Structural PDF Layout Healer running on http://127.0.0.1:5003")
    app.run(port=5003, debug=True)