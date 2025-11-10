# Configuration

The application uses **Pydantic Settings** for type-safe configuration management with automatic environment variable loading and validation.

## Environment Variables

Create a `.env` file in the project root with your configuration:

```env
# =================================================================
# AI PROVIDER CONFIGURATION
# =================================================================
AI_PROVIDER=openai                    # AI provider (openai, azure, ollama, github)

# =================================================================
# OPENAI CONFIGURATION
# =================================================================
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.1
OPENAI_TIMEOUT=30

# =================================================================
# AZURE OPENAI CONFIGURATION  
# =================================================================
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment

# =================================================================
# OLLAMA CONFIGURATION
# =================================================================
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
OLLAMA_TIMEOUT=30

# =================================================================
# GITHUB MODELS CONFIGURATION
# =================================================================
GITHUB_TOKEN=ghp_your-github-token
GITHUB_MODEL=gpt-4o-mini
GITHUB_API_URL=https://models.inference.ai.azure.com

# =================================================================
# WEB FETCHER CONFIGURATION
# =================================================================
FETCHER_TIMEOUT=30                    # Request timeout in seconds
FETCHER_MAX_SIZE=10485760            # Max content size (10MB)
FETCHER_USER_AGENT=Mozilla/5.0 (compatible; AI-Recipe-Crawler/1.0)
FETCHER_CACHE_TTL=3600               # Cache TTL in seconds

# =================================================================
# SERVER CONFIGURATION
# =================================================================
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# =================================================================
# LOGGING CONFIGURATION
# =================================================================
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log
LOG_DEBUG_ENABLED=false

# =================================================================
# STORAGE CONFIGURATION
# =================================================================
BLOB_STORAGE_ENABLED=true            # Enable/disable blob storage
BLOB_STORAGE_BASE_PATH=tmp/storage   # Base path for blob storage
CACHE_ENABLED=true                   # Enable/disable memory caching
CACHE_MAX_SIZE=100                   # Maximum cache entries
CACHE_DEFAULT_TTL=3600              # Default cache TTL in seconds

# =================================================================
# RETRY CONFIGURATION
# =================================================================
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=60.0

# Provider-specific retry settings
OPENAI_MAX_RETRIES=3
GITHUB_MAX_RETRIES=3
GITHUB_RPM_LIMIT=15                  # GitHub has strict rate limits
```

## Configuration Features

- **Type Safety**: All configuration values are validated and type-checked
- **Environment Variables**: Automatic loading from `.env` files
- **Validation**: Invalid values are caught early with clear error messages
- **Documentation**: Each setting includes description and default values
- **Organized Sections**: Configuration grouped by functionality
- **Backward Compatibility**: Maintains same variable names as before

## Configuration Access

The configuration system provides both modern Pydantic access and backward-compatible exports:

```python
# Modern Pydantic access
from app.config.pydantic_config import settings
print(settings.openai.api_key)
print(settings.web_fetcher.timeout)

# Backward-compatible access (recommended for existing code)
from app.config.pydantic_config import OPENAI_API_KEY, FETCHER_TIMEOUT
print(OPENAI_API_KEY)
print(FETCHER_TIMEOUT)
```

## Store Configuration

The application supports multiple grocery stores with configurable adapters:

- **Coles**: Australian supermarket chain
- **Woolworths**: Australian supermarket chain  
- **ALDI**: International discount supermarket
- **IGA**: Independent Grocers of Australia

Store configurations include:
- Search URL patterns
- HTML selectors for product extraction
- Product page URL patterns
- Store-specific data processing

For production use:
1. Configure store-specific search mechanisms in `app/config/store_config.py`
2. Implement real web scraping or API integration
3. Add store API keys to environment variables if required

## Configuration Best Practices

### Environment Files

- Keep `.env` files secure and never commit them to version control
- Use `.env.example` templates for team sharing
- Consider using separate `.env` files for different environments (development, staging, production)

### Security Considerations

- Store sensitive values like API keys in environment variables
- Use secure secret management systems in production
- Rotate API keys regularly
- Limit API key permissions to minimum required scope

### Performance Tuning

- Adjust timeout values based on your network conditions
- Configure cache settings based on available memory
- Set appropriate retry limits to balance reliability and performance
- Monitor rate limits for external services

### Debugging Configuration Issues

1. **Check Environment Variables**: Ensure all required variables are set
2. **Validate Configuration**: Use Pydantic validation errors to identify issues
3. **Test API Keys**: Verify API keys work with simple test requests
4. **Review Logs**: Check application logs for configuration-related errors
5. **Use Default Values**: Start with default configuration and customize gradually

### Environment-Specific Configuration

#### Development
```env
LOG_LEVEL=DEBUG
LOG_DEBUG_ENABLED=true
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
```

#### Production
```env
LOG_LEVEL=INFO
LOG_TO_FILE=true
AI_PROVIDER=openai
OPENAI_MAX_RETRIES=5
RETRY_MAX_ATTEMPTS=5
```

#### Testing
```env
LOG_LEVEL=WARNING
AI_PROVIDER=stub
CACHE_ENABLED=false
BLOB_STORAGE_ENABLED=false
```