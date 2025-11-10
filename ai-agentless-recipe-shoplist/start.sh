#!/bin/bash

# AI Recipe Shoplist Crawler - Startup Script
# Updated for Pydantic configuration system
# Features: Type-safe config validation, automatic directory creation, flexible server config

echo "🤖 AI Recipe Shoplist Crawler - Starting Application"
echo "================================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python version: $python_version"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
fi

# Sync dependencies with uv
echo "� Syncing dependencies with uv..."
uv sync

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create a .env file with your configuration."
    echo "Example .env file:"
    echo ""
    echo "# AI Provider (openai, azure, ollama, github)"
    echo "AI_PROVIDER=openai"
    echo ""
    echo "# OpenAI Configuration"
    echo "OPENAI_API_KEY=sk-your-openai-key-here"
    echo "OPENAI_MODEL=gpt-4o-mini"
    echo ""
    echo "# Or Azure OpenAI Configuration"  
    echo "# AZURE_OPENAI_API_KEY=your-azure-key"
    echo "# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
    echo "# AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment"
    echo ""
    echo "# Or Ollama Configuration"
    echo "# OLLAMA_HOST=http://localhost:11434"
    echo "# OLLAMA_MODEL=llama3.1"
    echo ""
    echo "# Or GitHub Models Configuration"
    echo "# GITHUB_TOKEN=ghp_your-github-token"
    echo "# GITHUB_MODEL=gpt-4o-mini"
    echo ""
    echo "For more details, see the README.md file."
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
        ollama_host=$(grep "^OLLAMA_HOST=" .env | cut -d'=' -f2 | sed 's/[[:space:]]*$//')
        if [ -z "$ollama_host" ]; then
            ollama_host="http://localhost:11434"
        fi
        if ! curl -s $ollama_host/api/tags > /dev/null; then
            echo "❌ Ollama is not running at $ollama_host"
            echo "Please start it with: ollama serve"
            exit 1
        fi
        echo "✓ Ollama is running at $ollama_host"
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
mkdir -p logs
mkdir -p tmp/web_cache
mkdir -p generated_bills

# Validate configuration using Python
echo "🔧 Validating configuration..."
uv run python -c "
import sys
sys.path.append('.')
try:
    from app.config.pydantic_config import settings, validate_required_config
    missing = validate_required_config()
    if missing:
        print('❌ Missing required configuration:')
        for key in missing:
            print(f'  - {key}')
        sys.exit(1)
    else:
        print('✓ Configuration is valid')
        print(f'✓ AI Provider: {settings.ai_provider.provider}')
        print(f'✓ Server: {settings.server.host}:{settings.server.port}')
        print(f'✓ Log Level: {settings.logging.level}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "Please fix the configuration errors above and try again."
    exit 1
fi

# Start the application
echo ""
echo "🚀 Starting FastAPI application..."
echo "📝 API Documentation: http://localhost:8000/api/docs"
echo "🌐 Web Interface: http://localhost:8000"
echo "📊 Alternative API Docs: http://localhost:8000/api/redoc"
echo ""
echo "📁 Log files will be written to: logs/app.log"
echo "💾 Cache directory: tmp/web_cache"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Get server configuration
server_host=$(grep "^SERVER_HOST=" .env | cut -d'=' -f2 | sed 's/[[:space:]]*$//')
server_port=$(grep "^SERVER_PORT=" .env | cut -d'=' -f2 | sed 's/[[:space:]]*$//')

# Use defaults if not specified
if [ -z "$server_host" ]; then
    server_host="0.0.0.0"
fi
if [ -z "$server_port" ]; then
    server_port="8000"
fi

# Run with uv and uvicorn
exec uv run uvicorn app.main:app --reload --host "$server_host" --port "$server_port"