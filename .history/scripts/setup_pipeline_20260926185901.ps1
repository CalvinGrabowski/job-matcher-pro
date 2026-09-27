# setup_pipeline.ps1

Write-Host "Launching Microservices silently in the background..." -ForegroundColor Green

# Filler Word Remover (Port 5001)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd ../services/filler_word_remover; python remover_service.py"

# Section Parser (Port 5002)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd ../services/section_parser; python snipper_service.py"

# Text Correction (Port 5003)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd ../services/text_correction; python correction_service.py"

# PDF-to-Text (Port 5004)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd ../services/pdf_to_text; python pdf_service.py"

Write-Host "All services are running." -ForegroundColor Cyan