# Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Prerequisites
- Python 3.11+ installed
- pip package manager

### Setup Steps

1. **Create Virtual Environment:**
   ```bash
   cd ai-recipe-shoplist
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or venv\Scripts\activate  # On Windows
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AI Provider:**
   ```bash
   # Copy unified configuration template
   cp .env.example .env
   
   # Edit .env and choose your AI provider:
   # AI_PROVIDER=github    # Free tier
   # AI_PROVIDER=openai    # Paid service  
   # AI_PROVIDER=azure     # Enterprise
   # AI_PROVIDER=ollama    # Local/free
   ```

4. **Add API Credentials (choose one):**
   ```bash
   # For GitHub Models (free)
   GITHUB_TOKEN=your_github_token_here
   
   # For OpenAI (paid)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # For Azure OpenAI (enterprise)
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   
   # For Ollama (local - no API key needed)
   # Install Ollama first: https://ollama.ai
   # Then: ollama pull llama3.2:3b
   ```

5. **Start the Application:**
   ```bash
   python app/main.py
   ```

6. **Open Browser:** http://localhost:8000

### Docker Alternative

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your AI provider and credentials
   ```

2. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

3. **Open Browser:** http://localhost:8000

## 🧪 Test the Application

1. Click "Try Demo" to load a sample recipe
2. Or enter a recipe URL from popular sites
3. Watch the AI extract ingredients and optimize shopping
4. Generate PDF/HTML bills with cost breakdowns

## 🔧 AI Provider Details

### GitHub Models (Free Tier)
- **Get Token:** https://github.com/settings/tokens
- **Cost:** Free during preview
- **Rate Limit:** 15 requests/minute
- **Best For:** Testing and development

### OpenAI (Paid Service)
- **Get API Key:** https://platform.openai.com/api-keys
- **Cost:** ~$0.01-0.03 per recipe
- **Rate Limit:** 60 requests/minute
- **Best For:** Production use

### Azure OpenAI (Enterprise)
- **Setup:** https://portal.azure.com
- **Cost:** Enterprise pricing
- **Rate Limit:** 120 requests/minute
- **Best For:** Large-scale deployment

### Ollama (Local/Free)
- **Install:** https://ollama.ai
- **Setup:** `ollama pull llama3.2:3b`
- **Cost:** Free (uses local compute)
- **Best For:** Privacy-focused or offline use

## 🔍 Troubleshooting

### Dependency Issues
```bash
# Try minimal install first
pip install -r requirements-minimal.txt

# Clear cache and reinstall
pip cache purge
pip install --force-reinstall --no-cache-dir -r requirements.txt
```

### Configuration Issues
```bash
# Test configuration loading
python test_tenacity_retry.py

# Check available AI providers
grep "AI_PROVIDER=" .env.example
```

### Common Fixes
```bash
# Update pip
pip install --upgrade pip

# Check package conflicts
pip check

# Test core imports
python -c "import fastapi, tenacity; print('✅ Core packages OK')"
```

## 📝 Features

- 🤖 **AI-Powered**: Intelligent recipe analysis and ingredient extraction
- 🛒 **Multi-Store Shopping**: Optimizes purchases across different stores
- 💰 **Cost Optimization**: Finds best prices and minimizes total cost
- 📄 **Smart Bills**: Generates detailed PDF/HTML shopping lists
- 🔄 **Retry Logic**: Production-ready error handling with tenacity
- ⚙️ **Unified Config**: Single `.env` file for all providers

## 🚀 Next Steps

1. Visit http://localhost:8000 for the web interface
2. Check http://localhost:8000/docs for API documentation
3. Explore different AI providers in `.env`
4. Customize retry settings for your use case

Enjoy smart recipe shopping! 🛒🤖