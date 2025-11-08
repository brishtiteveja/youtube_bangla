#!/bin/bash

echo "🇧🇩 YouTube Transcript Collector - Bangladesh Edition"
echo "======================================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "⚠️  uv not found. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv pip install -r requirements.txt
echo ""

echo "🚀 Starting the application..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo ""
echo "✨ Features:"
echo "   - 1000 Bangladeshi Channels Database"
echo "   - Default: Pinaki Bhattacharya"
echo "   - Search any YouTube channel"
echo "   - Multi-language transcripts"
echo ""
echo "💡 To stop the app, press Ctrl+C"
echo ""

# Run with uv
uv run streamlit run app.py
