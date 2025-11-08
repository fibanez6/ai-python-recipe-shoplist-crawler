# Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Prerequisites
- Python 3.11+ installed
- pip package manager

### Option 1: Local Development

1. **Clone and setup:**
   ```bash
   cd ai-recipe-shoplist
   chmod +x start.sh
   ```

2. **Configure AI provider (choose one):**
   ```bash
   # For OpenAI
   cp .env.openai .env
   # Edit .env and add your OpenAI API key
   
   # For Ollama (local, free)
   cp .env.ollama .env
   # Install and start Ollama first:
   # curl -fsSL https://ollama.ai/install.sh | sh
   # ollama serve
   # ollama pull llama3.2:3b
   ```

3. **Start the application:**
   ```bash
   ./start.sh
   ```

4. **Open browser:** http://localhost:8000

### Option 2: Docker

1. **Create environment file:**
   ```bash
   cp .env.openai .env
   # Edit .env with your API key
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Open browser:** http://localhost:8000

## 🧪 Test the Application

1. Click "Try Demo" to load a sample recipe
2. Or enter a recipe URL like: `https://www.allrecipes.com/recipe/213742/cheesy-chicken-broccoli-casserole/`
3. Watch the AI extract ingredients and optimize shopping
4. Generate PDF/HTML bills

## 🔧 AI Provider Setup

### OpenAI (Recommended)
- Get API key: https://platform.openai.com/api-keys
- Models: gpt-4o-mini (fast), gpt-4o (better quality)
- Cost: ~$0.01-0.03 per recipe

### Azure OpenAI
- Create resource: https://portal.azure.com/
- Deploy model: gpt-4o-mini
- Good for enterprise use

### Ollama (Free, Local)
- Models: llama3.2:3b (fast), llama3.2:7b (better)
- No API costs, runs locally
- Requires ~4GB RAM

### GitHub Models (Beta)
- Access: https://github.com/marketplace/models
- Free during beta
- Various models available

## 📝 Notes

- Current grocery store data is mocked for demonstration
- For production, implement real store APIs in `store_crawler.py`
- The AI intelligently extracts ingredients and optimizes shopping across stores
- Bills include cost breakdowns and travel optimization

Enjoy smart recipe shopping! 🛒🤖