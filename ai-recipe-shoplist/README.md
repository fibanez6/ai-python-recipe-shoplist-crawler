# AI Recipe Shoplist Crawler

An intelligent Python 3.11+ application that crawls recipe websites, extracts ingredients using AI, searches multiple grocery stores for the best prices, and generates detailed shopping bills with cost optimization.

## 🚀 Features

- 🤖 **AI-Powered Recipe Extraction**: Uses OpenAI, Azure OpenAI, Ollama, or GitHub Models to intelligently parse recipe websites
- 🛒 **Multi-Store Price Comparison**: Searches Coles, Woolworths, ALDI, and IGA for best prices
- 🧠 **Smart Optimization**: AI-enhanced price optimization across multiple stores
- 🧾 **Bill Generation**: Creates formatted receipts in PDF, HTML, and JSON formats
- 🌐 **Modern Web Interface**: FastAPI-based web application with responsive design
- 📱 **Mobile-Friendly**: Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

```
ai-recipe-shoplist/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── models.py                   # Pydantic data models
│   ├── services/
│   │   ├── ai_service.py           # AI provider management
│   │   ├── recipe_crawler.py       # Recipe website scraping
│   │   ├── store_crawler.py        # Grocery store adapters
│   │   ├── price_optimizer.py      # Cost optimization logic
│   │   └── bill_generator.py       # Receipt generation
│   ├── templates/
│   │   └── index.html             # Web interface
│   └── static/
│       ├── style.css              # Styling
│       └── app.js                 # Frontend JavaScript
├── .env.openai                   # OpenAI configuration
├── .env.azure                    # Azure OpenAI configuration
├── .env.ollama                   # Ollama configuration
├── .env.github                   # GitHub Models configuration
├── .env.example                  # Environment template
├── requirements.txt              # Dependencies
├── pyproject.toml               # Python 3.11+ project config
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- pip
- One of the AI providers configured (see AI Provider Setup below)

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd ai-recipe-shoplist
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AI provider** (choose one):
   ```bash
   # Copy the appropriate environment file
   cp .env.openai .env     # For OpenAI
   cp .env.azure .env      # For Azure OpenAI  
   cp .env.ollama .env     # For Ollama
   cp .env.github .env     # For GitHub Models
   
   # Edit .env with your credentials
   nano .env
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open your browser:**
   ```
   http://localhost:8000
   ```

## 🤖 AI Provider Setup

### OpenAI

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copy `.env.openai` to `.env`
3. Set your API key:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   AI_PROVIDER=openai
   ```

### Azure OpenAI

1. Create Azure OpenAI resource in [Azure Portal](https://portal.azure.com/)
2. Deploy a model (e.g., gpt-4o-mini)
3. Copy `.env.azure` to `.env`
4. Configure:
   ```env
   AZURE_OPENAI_API_KEY=your-azure-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   AI_PROVIDER=azure
   ```

### Ollama (Local)

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Start Ollama and pull a model:
   ```bash
   ollama serve
   ollama pull llama3.2:3b
   ```

3. Copy `.env.ollama` to `.env`
4. Configure:
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b
   AI_PROVIDER=ollama
   ```

### GitHub Models

1. Request access at [GitHub Models](https://github.com/marketplace/models)
2. Create Personal Access Token with `repo` scope
3. Copy `.env.github` to `.env`
4. Configure:
   ```env
   GITHUB_TOKEN=ghp_your-token-here
   GITHUB_MODEL=gpt-4o-mini
   AI_PROVIDER=github
   ```

## 🌐 Usage

### Web Interface

1. **Navigate to http://localhost:8000**
2. **Enter a recipe URL** from supported sites:
   - AllRecipes.com
   - Food.com  
   - BBC Good Food
   - Any recipe site with structured data
3. **Click "Process Recipe"** to extract ingredients
4. **Review optimization results** showing best prices across stores
5. **Generate bills** in PDF, HTML, or JSON format

### API Endpoints

The application provides a RESTful API:

- `GET /` - Web interface
- `POST /api/process-recipe` - Extract recipe from URL
- `POST /api/optimize-shopping` - Complete optimization pipeline
- `POST /api/generate-bill` - Create shopping bill
- `GET /api/demo` - Load demo recipe
- `GET /api/stores` - List available stores
- `GET /api/docs` - API documentation

### Demo Mode

Try the demo with a sample recipe:
```bash
curl -X POST "http://localhost:8000/api/demo"
```

Or click "Try Demo" in the web interface.

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# AI Provider (openai, azure, ollama, github)
AI_PROVIDER=openai

# Application Settings
DEBUG=true
LOG_LEVEL=info
PORT=8000

# AI Configuration (set based on chosen provider)
OPENAI_API_KEY=your-key
# or
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
# or  
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
# or
GITHUB_TOKEN=your-token
GITHUB_MODEL=gpt-4o-mini
```

### Store Configuration

Currently uses mock adapters for demonstration. For production:

1. Replace mock adapters in `app/services/store_crawler.py`
2. Implement real store APIs or web scrapers
3. Add store API keys to environment variables

## 🧪 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black app/ tests/
isort app/ tests/
```

### Type Checking

```bash
mypy app/
```

### Adding New Features

1. **New Recipe Sites**: Extend `RecipeCrawler` in `recipe_crawler.py`
2. **New Stores**: Add adapters to `store_crawler.py`
3. **New AI Providers**: Implement `BaseAIProvider` in `ai_service.py`
4. **New Bill Formats**: Extend `BillGenerator` in `bill_generator.py`

## 📊 Optimization Strategies

The system uses multiple optimization strategies:

1. **Single Store**: Find cheapest single store option
2. **Multi-Store**: Optimize across all stores (may require multiple trips)
3. **AI-Enhanced**: Use AI to consider quality, travel costs, and substitutions

The AI optimizer considers:
- Product quality and brand reputation
- Travel costs between stores
- Bulk buying opportunities  
- Suitable ingredient substitutions

## 🎯 Example Workflow

1. **Input**: `https://allrecipes.com/recipe/123/chicken-stir-fry`
2. **AI Extraction**: 
   - Chicken breast (2 pieces)
   - Mixed vegetables (2 cups)
   - Soy sauce (3 tbsp)
   - Rice (1 cup)
3. **Store Search**:
   - Coles: Chicken $8.99, Vegetables $4.50, Soy sauce $3.20, Rice $2.80
   - Woolworths: Chicken $9.50, Vegetables $4.20, Soy sauce $3.50, Rice $2.90
   - ALDI: Chicken $7.99, Vegetables $3.80, Soy sauce $2.90, Rice $2.50
4. **Optimization**: Mix of ALDI (cheaper) + travel costs vs single store
5. **Bill Generation**: PDF receipt with itemized costs and store breakdown

## 🚀 Deployment

### Docker

```bash
docker build -t ai-recipe-shoplist .
docker run -p 8000:8000 --env-file .env ai-recipe-shoplist
```

### AWS Lambda

Use AWS SAM for serverless deployment:

```bash
sam build
sam deploy --guided
```

### Traditional Server

```bash
# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**AI Service Not Working**
- Verify API keys are correct
- Check internet connection for cloud providers
- For Ollama, ensure service is running: `ollama serve`

**Rate Limiting (429 Too Many Requests)**
- GitHub Models has strict rate limits - the app includes automatic retry logic
- Configure rate limiting settings in your `.env` file:
  ```bash
  GITHUB_RPM_LIMIT=15        # Requests per minute (default: 15)
  GITHUB_MAX_RETRIES=3       # Number of retries (default: 3)
  GITHUB_BASE_DELAY=1.0      # Base delay in seconds (default: 1.0)
  GITHUB_MAX_DELAY=60.0      # Maximum delay in seconds (default: 60.0)
  ```
- Consider switching to OpenAI or Azure for higher rate limits
- For production, implement request queuing to stay within limits

**No Products Found**
- Currently using mock data - this is expected
- Implement real store APIs for production use

**Bill Generation Fails**
- Install ReportLab: `pip install reportlab`
- Check file permissions in `generated_bills/` directory

**Web Interface Not Loading**
- Ensure templates and static directories exist
- Check FastAPI is serving static files correctly

### Getting Help

1. Check the [API documentation](http://localhost:8000/api/docs) when running
2. Review application logs for detailed error messages  
3. Try the demo mode to verify setup: `curl -X POST "http://localhost:8000/api/demo"`

## 🔮 Roadmap

- [ ] Real grocery store API integration
- [ ] Machine learning for better ingredient matching
- [ ] Multi-currency support
- [ ] Nutritional information integration
- [ ] User accounts and favorites
- [ ] Mobile app development
- [ ] Meal planning features
- [ ] Integration with shopping list apps

---

Built with ❤️ and AI in Python 3.11+