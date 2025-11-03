# Clinical AI Assistant - Streamlit Launcher
# Quick start script for Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Clinical AI Assistant - Streamlit UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

# Check if streamlit is installed
Write-Host "Checking dependencies..." -ForegroundColor Green
$streamlitInstalled = pip list | Select-String "streamlit"
if (-not $streamlitInstalled) {
    Write-Host "Installing Streamlit..." -ForegroundColor Yellow
    pip install streamlit
}

Write-Host ""
Write-Host "Starting Streamlit app..." -ForegroundColor Green
Write-Host "The app will open in your browser automatically." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Run streamlit
streamlit run app.py
