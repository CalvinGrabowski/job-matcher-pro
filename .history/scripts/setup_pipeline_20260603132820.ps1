# setup_pipeline.ps1 (Run from your personal '3. SPRING QUARTER' folder)

Write-Host "Launching Microservices silently in the background..." -ForegroundColor Green

# 1. Spin up Filler Word Remover (Port 5001)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd C361-Microservices/big_pool/filler_word_remover; python remover_service.py"

# 2. Spin up Section Snipper (Port 5002)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd C361-Microservices/big_pool/section_snipper; python snipper_service.py"

# 3. Spin up Layout Healer (Port 5003)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd C361-Microservices/big_pool/spell_correction; python correction_service.py"

# 3. Spin up Layout pdf-to-text (Port 5004)
Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", "cd C361-Microservices/small_pool/pdf_to_text; python pdf_service.py"

Write-Host "All services are running invisibly! Ready for pipeline requests." -ForegroundColor Cyan

