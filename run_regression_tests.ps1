# PowerShell script to automate frontend and backend regression tests

Write-Host "Running React frontend tests..."
Push-Location ./React/frontend
npm test -- --watchAll=false
Pop-Location

Write-Host "Running Python backend tests..."
pytest