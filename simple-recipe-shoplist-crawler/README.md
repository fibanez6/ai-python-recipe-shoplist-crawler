# Recipe Shoplist Crawler

Small Python project that fetches recipe webpages, extracts ingredients and instructions, normalizes ingredient names and quantities, builds a unified shopping list and searches grocery sites (Coles, Woolworths, Aldi) for matching products and prices. It chooses best store combinations and produces a bill with estimated prices and images.

This scaffold provides a working local UI and backend using FastAPI with simple mocked grocery search adapters.

> **📝 Note:** The grocery store search functionality is currently **mocked** for demonstration purposes. The application simulates real store responses with realistic product data, prices, and images. See the [Extending to real grocery APIs](#extending-to-real-grocery-apis) section for information on implementing actual store integrations.

## Screenshots

### Home Page - Recipe Input
<img src="app/doco/Recipes_ShoppingLists_index_page.png" alt="Recipe Input Interface" width="600">

The application features a clean, user-friendly interface where you can enter a recipe URL. The home page provides a simple form to input recipe URLs from popular cooking websites, making it easy to get started with generating your shopping list.

### Results Page - Generated Shopping List
<img src="app/doco/Recipes_ShoppingLists_result_page.png" alt="Shopping List Results" width="600">

After processing a recipe, the application displays a comprehensive shopping list with:
- **Extracted ingredients** with normalized quantities and units
- **Product matches** from multiple grocery stores (Coles, Woolworths, Aldi)
- **Price comparisons** to help you find the best deals
- **Store recommendations** for optimal shopping routes
- **Visual product images** for easy identification
- **Estimated total costs** broken down by store

## Why this exists
- Quick prototype to assemble recipe ingredients into a shopping list and estimate cost across grocery retailers.
- Streamlines meal planning by automating the tedious process of creating shopping lists
- Helps save money by comparing prices across different grocery stores
- Reduces food waste by providing accurate quantity calculations

## What is included

- **FastAPI backend** in `app/` - Modern, fast web framework for building APIs
- **Simple web UI** templates in `app/templates/` and static files in `app/static/`
- **Service layers**: fetcher, parser, normalizer, shopper, optimizer
- **Mock grocery adapters** for Coles/Woolworths/Aldi (replaceable with real scrapers or APIs)
- **AWS SAM template** `samtemplate.yaml` to deploy as a Lambda function behind API Gateway
- **Requirements file** `requirements.txt` for easy dependency management
- **Git ignore** configuration for clean repository management

## Features

### 🔍 **Smart Recipe Parsing**
- Extracts ingredients and instructions from recipe websites
- Normalizes ingredient names and quantities
- Handles various recipe formats and structures

### 🛒 **Multi-Store Shopping Optimization** 
- Searches across multiple grocery stores (Coles, Woolworths, Aldi)
- Compares prices and product availability
- Suggests optimal store combinations for cost savings

### 📊 **Price Analysis**
- Real-time price comparisons
- Cost breakdown by store
- Estimated total shopping costs

### 🎯 **User-Friendly Interface**
- Simple URL input for recipe processing
- Visual product images and store logos
- Clear shopping list organization

## Quickstart (local)

### Prerequisites
- Python 3.11+ (recommended: Python 3.13)
- pip package manager

### Installation & Setup

1. **Create and activate a Python virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the application:**

```bash
uvicorn app.main:app --reload --port 8000
```

4. **Open your browser and navigate to:**
   - **Web Interface:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

### Usage

1. Enter a recipe URL in the input field (try popular cooking websites like AllRecipes, Food.com, etc.)
2. Click "Generate Shopping List" 
3. Review the extracted ingredients and price comparisons
4. Use the generated shopping list for your grocery trip!

## Deploy with AWS SAM

### Prerequisites
- AWS CLI installed and configured
- SAM CLI installed
- Valid AWS credentials


### Deployment Steps

1. **Install and configure AWS CLI and SAM CLI:**
   - Follow the [AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
   - Install [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
   - Configure your AWS credentials with `aws configure`

2. **Configure deployment settings:**

```bash
cp samconfig.toml.template samconfig.toml
# Edit samconfig.toml with your preferred settings
```

3. **Validate, build, and deploy:**

```bash
# Validate the SAM template
sam validate --template-file samtemplate.yaml --lint

# Build the application
sam build --template-file samtemplate.yaml --use-container

# Deploy with guided setup (first time)
sam deploy --guided

# For subsequent deployments
sam deploy
```

## Architecture

The application follows a clean, modular architecture:

```
app/
├── main.py              # FastAPI application entry point
├── services/            # Business logic layer
│   ├── fetcher.py      # Web scraping and content retrieval
│   ├── parser.py       # Recipe parsing and extraction
│   ├── normalizer.py   # Ingredient normalization
│   ├── optimizer.py    # Price optimization algorithms
│   └── shopper/        # Store integration
├── templates/          # HTML templates
└── static/            # CSS, JS, and image assets
```

## Extending to real grocery APIs

### Current Implementation
The application currently uses mock adapters that simulate grocery store responses. These provide realistic data for testing and demonstration purposes.

### Real Store Integration
To integrate with actual grocery store APIs:

1. **Replace mock adapters** in `app/services/shopper/adapters.py` with real scrapers or SDK calls
2. **Implement authentication** for store APIs (API keys, OAuth, etc.)
3. **Handle rate limiting** and respect robots.txt policies
4. **Add error handling** for network issues and API changes
5. **Improve normalization** in `app/services/normalizer.py` for better product matching

### Supported Stores (Mock Implementation)
- 🛒 **Coles** - Australian supermarket chain
- 🏪 **Woolworths** - Major Australian grocery retailer  
- 🅰️ **Aldi** - Discount supermarket chain

## API Endpoints

The application provides several REST API endpoints:

- `GET /` - Main web interface
- `POST /api/process-recipe` - Process a recipe URL and extract ingredients
- `GET /api/health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML/CSS/JavaScript with Jinja2 templates
- **Deployment:** AWS Lambda + API Gateway (via SAM)
- **Dependencies:** See `requirements.txt` for complete list

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is available under the MIT License. See the LICENSE file for more details.

## Notes

- This project is a **scaffold and prototype** containing simple heuristics and mocks designed for easy extension
- The mock adapters provide realistic data for development and testing purposes
- The application demonstrates modern web development practices with FastAPI and clean architecture
- Perfect for learning about web scraping, API development, and cloud deployment
- Easily extensible to support additional grocery stores or international markets

## Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Review the logs for error details
3. Open an issue on GitHub with detailed information about the problem

---

**Happy cooking and shopping! 🍳🛒**
