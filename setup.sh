#!/bin/bash

# Instagram Carousel Generator Setup Script

echo "🚀 Setting up Instagram Carousel Generator..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Make script executable
chmod +x src/carousel_generator.py

echo ""
echo "🎉 Setup complete! Here's how to get started:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. List available topics:"
echo "   python src/carousel_generator.py --list"
echo ""
echo "3. Generate your first carousel:"
echo "   python src/carousel_generator.py --topic communication_tips"
echo ""
echo "4. Check the carousels/ directory for your images!"
echo ""
echo "Happy content creating! 🌟"