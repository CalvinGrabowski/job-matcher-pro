import os
import requests

# Configuration
TARGET_FOLDER = "read_pdfs"
URL = "http://127.0.0.1:5001/extract"

# 1. Ensure folder exists and find files
if not os.path.exists(TARGET_FOLDER):
    print(f"Error: The folder '{TARGET_FOLDER}' does not exist. Creating it now...")
    os.makedirs(TARGET_FOLDER)
    pdf_files = []
else:
    # List ALL files in the directory ending with .pdf
    pdf_files = [f for f in os.listdir(TARGET_FOLDER) if f.lower().endswith('.pdf')]

if not pdf_files:
    print(f"Error: No PDF files found in the '{TARGET_FOLDER}' directory to test.")
    print(f"Please drop one or more PDFs into the '{os.path.abspath(TARGET_FOLDER)}' folder.")
else:
    print(f"Found {len(pdf_files)} PDF file(s) in '{TARGET_FOLDER}'. starting batch extraction...\n")
    print(f"Connecting to microservice at: {URL}")
    print("\n" * 5)

    # 2. Loop through every single PDF file found
    for index, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(TARGET_FOLDER, filename)
        print(f"\n[{index}/{len(pdf_files)}] Processing: {filename}")
        
        try:
            # Open and stream the current file over the REST API
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(URL, files=files)
                
            # 3. Handle the response for this specific file
            if response.status_code == 200:
                print(f"--- Extraction Successful ({filename}) ---\n")
                text_content = response.json().get('text', 'No text returned.')
                # Print just the first 200 characters so your terminal doesn't get completely flooded
                print(text_content)
                print("\n\n This is only the first 500 characters \n\n")
            else:
                print(f"Server Error ({response.status_code}) on file {filename}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Lost connection to port 5001. Ensure pdf_service.py is still running.")
            break # Stop loop if the server crashes or isn't running
        except Exception as e:
            print(f"An unexpected error occurred while processing {filename}: {e}")

    print("\n" * 5)
    print("Batch processing complete!")