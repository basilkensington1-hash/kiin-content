#!/bin/bash

# Kiin Content Factory Dashboard Launcher
# 🚀 Your beautiful dashboard awaits!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🎬 Welcome to Kiin Content Factory Dashboard${NC}"
echo -e "${PURPLE}════════════════════════════════════════════${NC}"

# Change to the dashboard directory
cd "$SCRIPT_DIR"

# Check if we're in the right place
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found. Are you in the right directory?${NC}"
    exit 1
fi

# Check for virtual environment in parent directory
VENV_PATH="$PROJECT_DIR/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}🔧 Virtual environment not found. Creating one...${NC}"
    cd "$PROJECT_DIR"
    python3 -m venv venv
    
    echo -e "${YELLOW}📦 Installing parent project dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    
    cd "$SCRIPT_DIR"
else
    echo -e "${GREEN}✅ Found virtual environment${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Install Flask if not present
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing Flask...${NC}"
    pip install flask
fi

# Check if the parent project requirements are met
cd "$PROJECT_DIR"
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}🔍 Checking project dependencies...${NC}"
    pip install -r requirements.txt --quiet
fi

# Return to dashboard directory
cd "$SCRIPT_DIR"

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Check if port 5000 is available
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null; then
    echo -e "${YELLOW}⚠️  Port 5000 is already in use. Trying port 5001...${NC}"
    PORT=5001
else
    PORT=5000
fi

echo -e "${GREEN}🚀 Starting Kiin Content Factory Dashboard...${NC}"
echo -e "${BLUE}📱 Dashboard URL: http://localhost:$PORT${NC}"
echo -e "${PURPLE}════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Click any 'Generate Video' button to create content"
echo -e "   • The dashboard shows your available stories and recent videos"
echo -e "   • Videos are saved to: $PROJECT_DIR/output/"
echo -e "   • Press Ctrl+C to stop the server"
echo ""
echo -e "${GREEN}🎬 Ready to create amazing caregiver content!${NC}"
echo ""

# Start the Flask development server
if [ "$PORT" = "5001" ]; then
    python app.py --port 5001 &
    SERVER_PID=$!
else
    python app.py &
    SERVER_PID=$!
fi

# Wait a moment for server to start
sleep 2

# Try to open the browser (macOS/Linux)
if command -v open >/dev/null 2>&1; then
    echo -e "${BLUE}🌐 Opening dashboard in your browser...${NC}"
    open "http://localhost:$PORT"
elif command -v xdg-open >/dev/null 2>&1; then
    echo -e "${BLUE}🌐 Opening dashboard in your browser...${NC}"
    xdg-open "http://localhost:$PORT"
else
    echo -e "${YELLOW}📍 Please open http://localhost:$PORT in your browser${NC}"
fi

# Wait for the server process
wait $SERVER_PID