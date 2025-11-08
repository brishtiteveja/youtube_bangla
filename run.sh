#!/bin/bash

# Get port from command line argument, default to 8890
PORT=${1:-8890}

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

echo "🚀 Starting the application on port $PORT..."
echo "📱 The app will open in your browser at http://localhost:$PORT"
echo ""
echo "✨ Features:"
echo "   - 1000 Bangladeshi Channels Database"
echo "   - Default: Pinaki Bhattacharya"
echo "   - Search any YouTube channel"
echo "   - Multi-language transcripts"
echo ""
echo "💡 To stop the app, press Ctrl+C"
echo "💡 Usage: ./run.sh [port]  (default port: 8890)"
echo ""

# Run with uv on specified port
uv run streamlit run app.py --server.port=$PORT
