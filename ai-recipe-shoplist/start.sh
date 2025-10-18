#!/bin/bash

# AI Recipe Shoplist Crawler - Startup Script

echo "🤖 AI Recipe Shoplist Crawler - Starting Application"
echo "================================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please copy one of the example files:"
    echo "  cp .env.openai .env    (for OpenAI)"
    echo "  cp .env.azure .env     (for Azure OpenAI)"
    echo "  cp .env.ollama .env    (for Ollama)"
    echo "  cp .env.github .env    (for GitHub Models)"
    echo ""
    echo "Then edit .env with your API keys and configuration."
    exit 1
fi

# Check AI provider configuration
ai_provider=$(grep "^AI_PROVIDER=" .env | cut -d'=' -f2)
echo "🧠 AI Provider: $ai_provider"

# Validate AI provider configuration
case $ai_provider in
    "openai")
        if ! grep -q "^OPENAI_API_KEY=" .env; then
            echo "❌ OpenAI API key not found in .env file"
            exit 1
        fi
        echo "✓ OpenAI configuration found"
        ;;
    "azure")
        if ! grep -q "^AZURE_OPENAI_API_KEY=" .env; then
            echo "❌ Azure OpenAI configuration not found in .env file"
            exit 1
        fi
        echo "✓ Azure OpenAI configuration found"
        ;;
    "ollama")
        echo "🔍 Checking if Ollama is running..."
        if ! curl -s http://localhost:11434/api/tags > /dev/null; then
            echo "❌ Ollama is not running. Please start it with: ollama serve"
            exit 1
        fi
        echo "✓ Ollama is running"
        ;;
    "github")
        if ! grep -q "^GITHUB_TOKEN=" .env; then
            echo "❌ GitHub token not found in .env file"
            exit 1
        fi
        echo "✓ GitHub Models configuration found"
        ;;
    *)
        echo "❌ Unknown AI provider: $ai_provider"
        echo "Valid options: openai, azure, ollama, github"
        exit 1
        ;;
esac

# Create necessary directories
mkdir -p generated_bills

# Start the application
echo ""
echo "🚀 Starting FastAPI application..."
echo "📝 API Documentation: http://localhost:8000/api/docs"
echo "🌐 Web Interface: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000