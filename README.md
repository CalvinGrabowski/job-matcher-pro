# Job Matcher Pro

Job Matcher Pro is a full-stack application that analyzes resumes, cover letters, and job descriptions to evaluate application strength and identify opportunities for improvement.

The platform extracts text from PDF documents, performs document processing through a microservice architecture, and generates keyword alignment metrics, missing skill recommendations, and application matching insights to help users better tailor their applications for specific positions.

---

## Features

- Resume upload and analysis
- Cover letter upload and analysis
- Job description parsing
- PDF text extraction
- Keyword alignment scoring
- Missing keyword identification
- ATS-focused application review
- Interactive document comparison interface
- Modular microservice architecture

---

## Why I Built This

As a student actively applying for internships and software engineering positions, I found it difficult to understand how well my application materials aligned with specific job descriptions.

I built Job Matcher Pro to automate that process by providing objective feedback on resumes and cover letters, highlighting missing skills, identifying keyword gaps, and visualizing overall application alignment.

---

## Technologies Used

### Languages
- Python
- HTML
- CSS
- JavaScript

### Frameworks & Libraries
- Flask
- Requests
- PyPDF2

### Concepts
- Microservices
- REST APIs
- PDF Processing
- Text Analysis
- Application Scoring
- ATS Optimization

---

## Architecture

The application consists of a central Flask web application that coordinates multiple independent microservices.

```text
Resume PDF
      \
Cover Letter ---> Main Web Application ---> Match Analysis
      /                     |
Job Description             |
                            v
                     PDF-to-Text Service
                            |
                            v
                   Document Processing Services
                            |
                            v
                      Alignment Results
```

### Services

- PDF-to-Text Extraction
- Filler Word Removal
- Section Parsing
- Text Correction

Each service operates independently and communicates through HTTP requests.

---

## Screenshots

### Match Analysis Dashboard

Displays:

- Keyword Alignment Matrix
- Missing Skills Analysis
- Resume-to-Job Comparison
- Cover Letter Evaluation

(Add screenshots here)

---

## Project Structure

```text
job-matcher-pro/
│
├── README.md
├── scripts/
│   ├── setup_pipeline.ps1
│   ├── run_main.ps1
│   ├── stop_pipeline.ps1
│   └── check_pipeline.ps1
│
├── app/
│   ├── app.py
│   └── templates/
│
├── services/
│   ├── pdf_to_text/
│   ├── filler_word_remover/
│   ├── section_parser/
│   └── text_correction/
│
└── docs/
    └── screenshots/
```

---

## Running the Application

Start all microservices:

From the main directory, you can do these commands, or navigate to the scripts file and remove the \scripts part of the commands.

```powershell
.\scripts\setup_pipeline.ps1
```

Launch the main application:

```powershell
.\scripts\run_main.ps1
```

Verify services are active:

```powershell
.\scripts\check_pipeline.ps1
```

Stop all services:

```powershell
.\scripts\stop_pipeline.ps1
```

---

## Future Improvements

- LLM-based resume feedback
- Semantic matching beyond keyword overlap
- Industry-specific scoring models
- Resume revision recommendations
- Cloud deployment
- User accounts and saved analyses

---

## Author

**Calvin Grabowski**

- Portfolio: https://calvingrabowski.github.io
- LinkedIn: https://linkedin.com/in/calvin-grabowski
- GitHub: https://github.com/CalvinGrabowski
