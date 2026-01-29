#!/bin/bash
# Quick launch for Kiin Automation Panel

cd "$(dirname "$0")"

echo "🎮 Starting Kiin Automation Panel..."
echo ""

# Use the venv
source venv/bin/activate

# Launch the panel
cd ..
python dashboard/automation_panel.py --port ${1:-5002}
