# One-command environment setup (Windows / PowerShell).
# Usage:  ./setup.ps1
# Creates a Python 3.12 virtual env in .venv and installs dependencies.

$ErrorActionPreference = "Stop"

# Pick Python 3.12 via the py launcher if available, else fall back to `python`.
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $py = "py -3.12"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $py = "python"
    Write-Host "WARNING: 'py -3.12' not found; using default 'python'. Confirm it is 3.12." -ForegroundColor Yellow
} else {
    throw "No Python found. Install Python 3.12 from python.org first."
}

Write-Host "Creating virtual environment in .venv ..." -ForegroundColor Cyan
Invoke-Expression "$py -m venv .venv"

Write-Host "Upgrading pip and installing requirements ..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from template - add your DEEPSEEK_API_KEY." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done. Activate with:  .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "Then run tests:        pytest -q" -ForegroundColor Green
