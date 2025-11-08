# Installation & Setup Guide

## Quick Start

### 1. Install Python 3.11+
Make sure you have Python 3.11 or newer installed:
```bash
python3 --version
# Should show Python 3.11.x or newer
```

### 2. Create Virtual Environment
```bash
cd ai-recipe-shoplist
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

#### Option A: Minimal Installation (Recommended to start)
```bash
pip install -r requirements-minimal.txt
```

#### Option B: Full Installation (if you need all features)
```bash
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
# Copy and edit your preferred AI provider config
cp .env.openai.example .env
# Edit .env with your actual API keys
```

### 5. Run the Application
```bash
python main.py
```

Visit `http://localhost:8000` in your browser.

## AI Provider Setup

### OpenAI (Recommended for beginners)
1. Get API key from https://platform.openai.com/
2. Copy `.env.openai.example` to `.env`
3. Set `OPENAI_API_KEY=your_key_here`

### Azure OpenAI
1. Set up Azure OpenAI service
2. Copy `.env.azure.example` to `.env`
3. Configure Azure endpoint and deployment names

### Ollama (Local AI - No API key needed)
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama2`
3. Copy `.env.ollama.example` to `.env`

### GitHub Models
1. Get access to GitHub Models (Preview)
2. Copy `.env.github.example` to `.env`
3. Set your GitHub token

## Troubleshooting

### Dependency Issues
If you get package conflicts:
1. Try the minimal requirements first: `pip install -r requirements-minimal.txt`
2. Update pip: `pip install --upgrade pip`
3. Use a fresh virtual environment

### Common Fixes
```bash
# Clear pip cache
pip cache purge

# Force reinstall
pip install --force-reinstall --no-cache-dir -r requirements-minimal.txt

# Check for conflicts
pip check
```

### Test Installation
```bash
# Quick test
python -c "import fastapi, openai, beautifulsoup4; print('✅ Core packages installed')"

# Full test
python main.py --help
```

## Docker Alternative
If you prefer Docker:
```bash
# Build and run with Docker
docker build -t recipe-crawler .
docker run -p 8000:8000 --env-file .env recipe-crawler
```

## Next Steps
1. Visit the web interface at http://localhost:8000
2. Try the sample recipe: paste a recipe URL or text
3. Check the API documentation at http://localhost:8000/docs
4. Explore the different AI providers in your .env file

## Support
- Check the README.md for detailed features
- Look at the example .env files for configuration options
- Use the minimal requirements if you encounter dependency issues