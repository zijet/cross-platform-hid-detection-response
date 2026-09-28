#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk libnotify-bin
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Installation complete."
echo "Run: source .venv/bin/activate"
echo "Then: python simulate_scenarios.py"
echo "Then: python run_agent.py"
