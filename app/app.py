from flask import Flask, render_template, request, flash, redirect, url_for, session
import requests
import re

app = Flask(__name__)

app.secret_key = 'super_secret_key_for_flash_system'

PDF_EXTRACTOR_URL = "http://127.0.0.1:5004/extract"
SPELL_CORRECTOR_URL = "http://127.0.0.1:5003/process"
SNIPPER_URL = "http://127.0.0.1:5002/process"
MATRIX_URL = "http://127.0.0.1:5001/matrix" 

@app.route('/', methods=['GET', 'POST'])
def index():
    # 1. Look for text saved from a failed validation check first
    job_text = session.pop('failed_job', None) or request.form.get('job', '')
    resume_text = session.pop('failed_resume', None) or request.form.get('resume', '')
    cover_letter = session.pop('failed_cover_letter', None) or request.form.get('cover_letter', '')
    
    return render_template('index.html', job=job_text, resume=resume_text, cover_letter=cover_letter)

@app.route('/analyze', methods=['POST'])
def analyze():
    job_raw = request.form.get('job', '')
    resume_text = request.form.get('resume', '')
    cover_letter_text = request.form.get('cover_letter', '')
    
    # Resume reading
    if 'resume_file' in request.files and request.files['resume_file'].filename != '':
        resume_file = request.files['resume_file']
        try:
            files = {'file': (resume_file.filename, resume_file.stream, resume_file.mimetype)}
            resume_text = requests.post(PDF_EXTRACTOR_URL, files=files).json().get("text", "")
        except Exception:
            pass

    # Cover letter reading
    if 'cover_letter_file' in request.files:
        cl_file = request.files['cover_letter_file']
        if cl_file.filename != '':
            try:
                cl_files = {'file': (cl_file.filename, cl_file.stream, cl_file.mimetype)}
                extractor_resp = requests.post(PDF_EXTRACTOR_URL, files=cl_files)
                cover_letter_text = extractor_resp.json().get("text") or ""
                print(f" -> Raw Cover Letter PDF Characters Extracted: {len(cover_letter_text)}")
            except Exception as e:
                print(f" Cover Letter PDF Extractor Failed: {e}")

    if not cover_letter_text:
        cover_letter_text = ""

    # If text is too short, save exactly what they typed before refreshing
    if len(resume_text.strip()) < 10 or len(job_raw.strip()) < 10:
        session['failed_job'] = job_raw
        session['failed_resume'] = resume_text
        session['failed_cover_letter'] = cover_letter_text
        
        flash("Please provide a more substantial Resume and Job Description text before analyzing.", "warning")
        return redirect(url_for('index'))
    
    # heal with correction service  
    try:
        resume_text = requests.post(SPELL_CORRECTOR_URL, json={"text": resume_text}).json().get("corrected_text", resume_text)
    except Exception:
        pass

    # Job description Boundry
    target_job_text = job_raw
    try:
        snipper_response = requests.post(SNIPPER_URL, json={"text": job_raw})
        response_json = snipper_response.json()
        print(f"[STAGE 3 DEBUG] Snipper Response Keys: {list(response_json.keys())}")
        
        if response_json.get("has_content") and response_json.get("requirements_section_only"):
            target_job_text = response_json.get("requirements_section_only").strip()
            print(f"Snipped Text Length: {len(target_job_text)} characters.")
        else:
            print("Warning JSON keys present, but conditions not met. Falling back to raw text.")
    except Exception as e:
        print(f" [STAGE 3 FAILURE] Snipper communication failed: {e}")

    # pipeline connection and matrix calculations
    full_application_text = resume_text.strip()
    if cover_letter_text.strip():
        full_application_text += "\n" + cover_letter_text.strip()

    try:
        matrix_resp = requests.post(MATRIX_URL, json={"job": target_job_text, "resume": full_application_text}).json()
        score = matrix_resp.get("score", 0)
        missing_keywords = matrix_resp.get("missing", [])
    except Exception as e:
        return f"<h3>Matrix Engine Error: {e}</h3>"

    # Initialize our display variable with the snipped job description text
    highlighted_job_desc = target_job_text

    # Highlight each word returned from the matrix microservice
    for keyword in missing_keywords:
        # Avoid running regex operations on empty fields
        if not keyword.strip():
            continue
        # Use regex word boundaries (\b) to match full words cleanly without breaking sub-strings
        compiled_keyword = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
        highlighted_job_desc = compiled_keyword.sub(r'<mark class="bg-warning text-dark px-1 rounded" style="--bs-bg-opacity: 0.4;">\1</mark>', highlighted_job_desc)

    # UI information
    return render_template('results.html', 
                            score=score, 
                            missing=missing_keywords, 
                            job_display=highlighted_job_desc, 
                            resume_display=resume_text, 
                            cl_display=cover_letter_text)

if __name__ == '__main__':
    app.run(debug=True, port=5000)