from flask import Flask, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re

try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

BASE_STOP_WORDS = set(stopwords.words('english'))
CUSTOM_FILLER = {
    "basic", "best", "company", "controls", "date", "employer", "equivalent", 
    "follow", "levels", "like", "maintain", "must", "nice", "policies", 
    "proper", "reputed", "sensitive", "stay",
    "able", "actively", "additional", "all", "ambitious", "applicant", 
    "applicants", "apply", "applying", "aspects", "bachelor", "bachelors", 
    "bachelor's", "belief", "candidate", "candidates", "changing", 
    "communicate", "complete", "components", "concepts", "consider", 
    "continuous", "core", "correctness", "create", "critical", 
    "cross-context", "cycle", "day", "days", "degree", "description", 
    "develop", "developer", "developing", "development", "discover", 
    "enabling", "engage", "engineer", "engineering", "engineers", 
    "ensure", "experience", "experiences", "exploratory", "exploring", 
    "extended", "familiarity", "following", "founded", "full", 
    "fundamentally", "future", "goal", "helpful", "highly", "hours", 
    "human", "humanity", "impact", "improvement", "including", 
    "initiative", "interested", "job", "key", "knowledge", "largest", 
    "leadership", "learning", "life", "look", "love", "make", "manner", 
    "master", "masters", "meet", "metrics", "month", "months", "needed", 
    "needs", "one", "operation", "operations", "part", "phd", "position", 
    "positions", "possible", "problems", "prove", "provide", "qualification", 
    "qualifications", "quantify", "ranging", "rather", "reality", 
    "required", "requirement", "requirements", "resilience", "responsibility", 
    "responsibilities", "responsible", "role", "roles", "school", "similar", 
    "simple", "skill", "skills", "smart", "solving", "success", 
    "successful", "suite", "take", "team", "teams", "thorough", "today", 
    "turns", "ultimate", "unit", "used", "want", "week", "weekends", 
    "weeks", "work", "working", "world", "year", "years"

}
FULL_BLACKLIST = BASE_STOP_WORDS.union(CUSTOM_FILLER)

def process_text_stream(text):
    if not text:
        return set(), {}
        
    normalized = text.lower().replace("\r", " ").replace("\n", " ").replace("\t", " ")
    normalized = normalized.replace("–", " ").replace("—", " ").replace("/", " / ")
    
    raw_words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9+/-]*\b|c\+\+|c#', normalized)
    
    cleaned_set = set()
    stem_to_original = {}
    
    for word in raw_words:
        clean_word = word.strip(".,!?\"'()•*-:;›/")
        if not clean_word:
            continue
            
        root_word = lemmatizer.lemmatize(clean_word, pos='v')
        root_word = lemmatizer.lemmatize(root_word, pos='n')
        
        if clean_word in FULL_BLACKLIST or root_word in FULL_BLACKLIST:
            continue
            
        stemmed_word = stemmer.stem(root_word)
        
        if len(stemmed_word) > 1 or stemmed_word == 'c':
            cleaned_set.add(stemmed_word)
            if stemmed_word not in stem_to_original or len(clean_word) < len(stem_to_original[stemmed_word]):
                stem_to_original[stemmed_word] = clean_word
                
    return cleaned_set, stem_to_original

@app.route('/matrix', methods=['POST'])
def calculate_matrix():
    data = request.get_json()
    job_text = data.get('job', '')
    resume_text = data.get('resume', '')
    
    # Process both symmetrically at identical speeds
    job_tokens, job_mapping = process_text_stream(job_text)
    resume_tokens, _ = process_text_stream(resume_text)
    
    missing_stems = job_tokens - resume_tokens
    
    missing_requirements = [job_mapping.get(stem, stem) for stem in missing_stems]
    missing_requirements.sort()
    
    if not job_tokens:
        score = 100.0
    else:
        matched_tokens = job_tokens & resume_tokens
        score = round((len(matched_tokens) / len(job_tokens)) * 100, 2)
        
    # Add total job tokens count to your return schema on port 5001
    return jsonify({
        "score": score,
        "missing": missing_requirements,
        "total_job_tokens": len(job_tokens)
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)