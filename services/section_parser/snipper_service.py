import re
from flask import Flask, request, jsonify

app = Flask(__name__)

def strip_html_tags(text):
    """Removes all HTML tags (e.g., <mark class="...">) from the text."""
    clean_pattern = re.compile(r'<[^>]+>')
    return re.sub(clean_pattern, '', text)

@app.route('/process', methods=['POST'])
def snip_job_description():
    data = request.get_json() or {}
    raw_text = data.get("text", "")
    
    if not raw_text:
        return jsonify({"has_content": False, "requirements_section_only": ""})
        
    # STRIP ANY EXISTING HTML JUNK IMMEDIATELY
    text = strip_html_tags(raw_text)
        
    start_pattern = re.compile(r'(what\s+you\s*’*\'*ll\s+do|qualifications|requirements|must\s+have)', re.IGNORECASE)
    end_pattern = re.compile(r'(pay\s+range|compensation|equal\s+opportunity|about\s+the\s+company|set\s+alert|see\s+more\s+jobs|show\s+more)', re.IGNORECASE)
    
    start_match = start_pattern.search(text)
    
    if start_match:
        start_index = start_match.start()
        end_match = end_pattern.search(text, pos=start_index)
        
        if end_match:
            snipped_content = text[start_index:end_match.start()].strip()
        else:
            snipped_content = text[start_index:].strip()
            
        return jsonify({
            "has_content": True,
            "requirements_section_only": snipped_content
        })
        
    return jsonify({
        "has_content": False,
        "requirements_section_only": text  
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True)