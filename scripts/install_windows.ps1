$ErrorActionPreference = "Stop"
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Installation complete."
Write-Host "Run: .\.venv\Scripts\Activate.ps1"
Write-Host "Then: python simulate_scenarios.py"
Write-Host "Then: python run_agent.py"
