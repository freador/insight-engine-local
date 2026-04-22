#!/bin/bash

echo "🚀 Initializing InsightEngine (SQLite Mode)..."

# 1. Install Dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Initialization complete!"
echo "------------------------------------------------"
echo "Next steps:"
echo "1. Ensure Ollama is running: 'ollama pull llama3'"
echo "2. Run the pipeline: 'python pipeline.py'"
echo "3. Start the Premium Dashboard: 'python app_web.py'"
echo "4. Access: http://127.0.0.1:5001"
echo "------------------------------------------------"
