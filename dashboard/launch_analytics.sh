#!/bin/bash

# Kiin Content Factory Analytics Dashboard Launcher
# Comprehensive analytics and management interface

echo "🚀 Starting Kiin Content Factory Analytics Dashboard..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📁 Project Directory: ${NC}$PROJECT_ROOT"
echo -e "${BLUE}📊 Dashboard Directory: ${NC}$SCRIPT_DIR"
echo ""

# Check if we're in the right directory
cd "$SCRIPT_DIR"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "   Please install Python 3 and try again."
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found:${NC} $(python3 --version)"

# Check for pip
if ! command_exists pip3; then
    echo -e "${RED}❌ pip3 is required but not installed.${NC}"
    echo "   Please install pip3 and try again."
    exit 1
fi

echo -e "${GREEN}✅ pip3 found${NC}"

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Create data directory if it doesn't exist
DATA_DIR="$PROJECT_ROOT/data"
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${YELLOW}📂 Creating data directory...${NC}"
    mkdir -p "$DATA_DIR"
    echo -e "${GREEN}✅ Data directory created${NC}"
fi

# Check and install Flask if needed
echo -e "${YELLOW}🔧 Checking Flask installation...${NC}"
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📦 Installing Flask...${NC}"
    pip3 install flask
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install Flask${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Flask installed${NC}"
else
    echo -e "${GREEN}✅ Flask already installed${NC}"
fi

# Check and install other required packages
echo -e "${YELLOW}🔧 Installing additional dependencies...${NC}"
pip3 install pathlib datetime >/dev/null 2>&1

# Check if main project requirements exist and install them
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}📦 Installing project requirements...${NC}"
    pip3 install -r "$REQUIREMENTS_FILE" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Project requirements installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some project requirements may have failed to install${NC}"
        echo -e "${YELLOW}   This shouldn't affect the dashboard functionality${NC}"
    fi
fi

# Find available port
PORT=5001
check_port() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

echo -e "${YELLOW}🌐 Finding available port...${NC}"
while check_port $PORT; do
    PORT=$((PORT + 1))
    if [ $PORT -gt 5010 ]; then
        echo -e "${RED}❌ Could not find available port between 5001-5010${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Using port: ${NC}$PORT"

# Create launch URL
LAUNCH_URL="http://localhost:$PORT"

echo ""
echo -e "${PURPLE}🎬 Kiin Content Factory Analytics Dashboard${NC}"
echo -e "${PURPLE}===========================================${NC}"
echo ""
echo -e "${CYAN}📊 Analytics Features:${NC}"
echo -e "   • Content Library Overview with charts"
echo -e "   • Interactive Content Calendar"
echo -e "   • Performance Metrics Dashboard"
echo -e "   • Content Generation Controls"
echo -e "   • Content Database Browser"
echo ""
echo -e "${CYAN}🎨 Design Features:${NC}"
echo -e "   • Kiin Brand Colors & Typography"
echo -e "   • Mobile-Responsive Interface"
echo -e "   • Dark Mode Support"
echo -e "   • Real-time Animations"
echo ""
echo -e "${CYAN}🚀 Starting server...${NC}"
echo -e "${GREEN}📱 Dashboard URL: ${NC}$LAUNCH_URL"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Use the sidebar to navigate between sections"
echo -e "   • Click 'Generate Video' to create new content"
echo -e "   • Use the calendar to schedule content"
echo -e "   • Browse and search content in the Database section"
echo ""

# Function to open URL in browser
open_browser() {
    sleep 2
    if command_exists open; then
        # macOS
        open "$LAUNCH_URL" 2>/dev/null
    elif command_exists xdg-open; then
        # Linux
        xdg-open "$LAUNCH_URL" 2>/dev/null
    elif command_exists start; then
        # Windows (Git Bash)
        start "$LAUNCH_URL" 2>/dev/null
    fi
}

# Open browser in background
open_browser &

# Start the analytics dashboard
echo -e "${GREEN}🎯 Analytics Dashboard is starting...${NC}"
echo -e "${YELLOW}📝 Press Ctrl+C to stop the server${NC}"
echo ""

# Start the enhanced Flask app
python3 enhanced_app.py --port $PORT

# Cleanup message
echo ""
echo -e "${YELLOW}👋 Analytics Dashboard stopped${NC}"
echo -e "${GREEN}✨ Thanks for using Kiin Content Factory!${NC}"
echo ""