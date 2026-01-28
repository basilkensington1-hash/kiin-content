#!/bin/bash
# Caregiver Confessions Generator - Quick Launch Script

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install edge-tts pillow
else
    source venv/bin/activate
fi

echo "🎬 Generating caregiver confession video..."

# Parse arguments
CONFESSION_ID=""
OUTPUT_NAME="confession_example.mp4"

while [[ $# -gt 0 ]]; do
    case $1 in
        --id)
            CONFESSION_ID="$2"
            shift 2
            ;;
        --output)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--id CONFESSION_ID] [--output OUTPUT_NAME]"
            echo ""
            echo "Options:"
            echo "  --id       Specific confession ID (1-17)"
            echo "  --output   Output filename (default: confession_example.mp4)"
            echo "  --help     Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Build command
CMD="python src/confession_generator.py --output \"$OUTPUT_NAME\""
if [ ! -z "$CONFESSION_ID" ]; then
    CMD="$CMD --confession-id $CONFESSION_ID"
fi

# Run generator
eval $CMD

echo ""
echo "✅ Video generated: output/$OUTPUT_NAME"
echo "📱 Ready for social media upload!"
echo ""
echo "Next steps:"
echo "  • Review the video: open output/$OUTPUT_NAME"
echo "  • Upload to your platform of choice"
echo "  • Add captions/hashtags as needed"