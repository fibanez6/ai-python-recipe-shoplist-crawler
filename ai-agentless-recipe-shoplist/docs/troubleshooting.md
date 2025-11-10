# Troubleshooting

This guide provides comprehensive troubleshooting solutions for common issues you may encounter when using the AI-Agentless Recipe Shoplist application.

## Quick Fixes

### Application Won't Start - Missing pydantic_settings Module

**Problem**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Solution**:
```bash
pip install --upgrade pip
pip install pydantic-settings>=2.0.0
```

**Alternative**: Reinstall all dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## Common Issues

### Missing Dependencies (pydantic_settings)

**Symptoms**: Application fails to start with module import errors

**Solutions**:
- If you see `ModuleNotFoundError: No module named 'pydantic_settings'`, run:
  ```bash
  pip install --upgrade pip
  pip install pydantic-settings>=2.0.0
  ```
- Or reinstall all dependencies:
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```

### AI Service Not Working

**Symptoms**: API calls fail, no recipe extraction, or AI responses

**Troubleshooting Steps**:
1. **Verify API Keys**: Ensure your API keys are correct and active
2. **Check Internet Connection**: Verify connectivity for cloud providers (OpenAI, Azure, GitHub)
3. **For Ollama**: Ensure the service is running locally:
   ```bash
   ollama serve
   ollama list  # Check available models
   ```
4. **Test API Keys**: Use simple test requests to verify connectivity
5. **Check Rate Limits**: Ensure you haven't exceeded API rate limits

### Rate Limiting (429 Too Many Requests)

**Symptoms**: HTTP 429 errors, request failures during high usage

**Understanding Rate Limits**:
- **GitHub Models**: Strict rate limits (15 requests/minute)
- **OpenAI**: Higher limits based on tier
- **Azure OpenAI**: Configurable limits per deployment

**Solutions**:
1. **Configure Rate Limiting Settings** in your `.env` file:
   ```env
   GITHUB_RPM_LIMIT=15        # Requests per minute (default: 15)
   GITHUB_MAX_RETRIES=3       # Number of retries (default: 3)
   GITHUB_BASE_DELAY=1.0      # Base delay in seconds (default: 1.0)
   GITHUB_MAX_DELAY=60.0      # Maximum delay in seconds (default: 60.0)
   ```

2. **Provider Alternatives**:
   - Consider switching to OpenAI or Azure for higher rate limits
   - Use Ollama for unlimited local processing

3. **Production Considerations**:
   - Implement request queuing to stay within limits
   - Use multiple API keys with load balancing
   - Cache results to reduce API calls

### No Products Found

**Symptoms**: Recipe processing succeeds but no matching products are found

**Troubleshooting Steps**:
1. **Check Ingredient Names**: Ensure ingredients are clear and specific
2. **Verify Store Configurations**: Check store setups in `app/config/store_config.py`
3. **Try Ingredient Variations**: Test with different ingredient names or descriptions
4. **Review AI Matching**: Check if the AI is correctly interpreting ingredients
5. **Store Availability**: Verify that the selected stores are accessible and responding

### Recipe Extraction Fails

**Symptoms**: Unable to extract ingredients from recipe URLs

**Common Causes & Solutions**:
1. **URL Accessibility**: Ensure the recipe URL is publicly accessible
2. **Structured Data**: Some sites require specific parsing logic for recipe data
3. **AI Provider Issues**: Verify the AI provider is working with simple tests
4. **Site Changes**: Recipe sites may change their HTML structure
5. **Content Type**: Ensure the URL contains actual recipe content

**Debugging Steps**:
```bash
# Test with the demo endpoint
curl -X GET "http://localhost:8000/api/v1/demo"

# Check logs for specific error messages
tail -f logs/app.log
```

### Store Search Issues

**Symptoms**: Store searches fail or return no results

**Troubleshooting Steps**:
1. **Verify Store Configurations**: Check `app/config/store_config.py`
2. **Network Connectivity**: Ensure stores are accessible from your network
3. **Review Application Logs**: Check for specific error messages during store searches
4. **Test Individual Stores**: Try searches with one store at a time
5. **Configuration Validation**: Ensure store selectors and URLs are correct

### Web Interface Not Loading

**Symptoms**: Browser shows errors or blank pages

**Common Solutions**:
1. **Check Templates Directory**: Ensure `app/templates/` exists with `index.html`
2. **Verify Static Files**: Check `app/static/` directory contains CSS and JS files
3. **FastAPI Configuration**: Ensure static file serving is configured correctly
4. **Dependencies**: Verify all required packages are installed
5. **Port Conflicts**: Check if port 8000 is available or change the port

### Storage System Issues

#### Missing aiofiles

**Problem**: `ModuleNotFoundError: No module named 'aiofiles'`

**Solution**:
```bash
pip install aiofiles
```

#### Storage Directory Not Created

**Problem**: Permission errors or storage failures

**Solutions**:
1. **Check Permissions**: Ensure write permissions for `BLOB_STORAGE_BASE_PATH`
2. **Create Directory**: Manually create the storage directory
   ```bash
   mkdir -p tmp/storage
   chmod 755 tmp/storage
   ```

#### Serialization Errors

**Problem**: Objects cannot be saved or loaded

**Troubleshooting**:
1. **Check Object Compatibility**: Verify objects are compatible with chosen format (JSON/Pickle/Joblib)
2. **Format Selection**: Use appropriate serialization format for your data type
3. **Pydantic Models**: Ensure Pydantic models are properly defined

#### Async Context Errors

**Problem**: `RuntimeError: no running event loop`

**Solution**: Ensure storage operations are called within async functions:
```python
# Correct usage
async def my_function():
    await storage_manager.save_data("key", data)

# Incorrect usage (will cause errors)
def my_function():
    storage_manager.save_data("key", data)  # Missing await
```

#### Memory Cache Full

**Problem**: Cache-related errors or degraded performance

**Solutions**:
1. **Increase Cache Size**: Modify `CACHE_MAX_SIZE` in configuration
2. **Reduce TTL**: Lower `CACHE_DEFAULT_TTL` for faster cache expiration
3. **Manual Cache Clearing**: Clear cache programmatically when needed

### Performance Issues

#### Slow File Operations

**Symptoms**: Application feels sluggish during file operations

**Solutions**:
1. **Verify Async Usage**: Ensure all storage operations use `await`
2. **Check Disk Performance**: Monitor disk I/O and available space
3. **Optimize File Sizes**: Consider compression for large data objects
4. **Use Appropriate Formats**: Choose efficient serialization formats

#### High Memory Usage

**Symptoms**: Application consumes excessive memory

**Troubleshooting**:
1. **Review Cache Settings**: Check memory cache configuration
2. **Use Disk Storage**: Store large objects on disk instead of memory
3. **Monitor Object Sizes**: Profile memory usage of stored objects
4. **Implement Cleanup**: Add periodic cleanup of old cached data

#### Disk Space Issues

**Symptoms**: Storage operations fail due to insufficient space

**Solutions**:
1. **Monitor Storage Directory**: Check available disk space regularly
2. **Implement Cleanup Policies**: Automatically remove old files
3. **Use Compression**: Enable compression for stored data
4. **Archive Old Data**: Move historical data to archive storage

## Getting Help

### Self-Diagnosis Steps

1. **Check API Documentation**: Visit http://localhost:8000/api/v1/docs when the app is running
2. **Review Application Logs**: Check detailed error messages in log files
3. **Test Demo Mode**: Verify basic functionality with the demo endpoint:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/demo"
   ```
4. **Validate Configuration**: Ensure all required environment variables are set
5. **Check Network Connectivity**: Verify internet access for cloud AI providers

### Log Analysis

**Log Locations**:
- **Console Output**: Standard application logs during startup and operation
- **File Logs**: Check `logs/app.log` if file logging is enabled
- **Error Logs**: Look for stack traces and detailed error messages

**Common Log Patterns**:
```bash
# Check for configuration errors
grep -i "config\|setting" logs/app.log

# Look for API-related issues
grep -i "api\|request\|response" logs/app.log

# Find storage-related problems
grep -i "storage\|cache\|blob" logs/app.log

# Identify AI provider issues
grep -i "openai\|azure\|ollama\|github" logs/app.log
```

### Testing Connectivity

#### Test AI Providers

**OpenAI**:
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}],"max_tokens":5}' \
     https://api.openai.com/v1/chat/completions
```

**Ollama**:
```bash
curl http://localhost:11434/api/generate \
     -d '{"model":"llama3.1","prompt":"Hello","stream":false}'
```

#### Test Application Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/api/v1/docs

# Demo functionality
curl -X GET http://localhost:8000/api/v1/demo
```

### Environment Validation

**Check Python Version**:
```bash
python --version  # Should be 3.11+
```

**Verify Dependencies**:
```bash
pip list | grep -E "(fastapi|pydantic|aiofiles|uvicorn)"
```

**Test Virtual Environment**:
```bash
which python  # Should point to your virtual environment
echo $VIRTUAL_ENV  # Should show your venv path
```

## Advanced Troubleshooting

### Debug Mode Configuration

Enable detailed debugging by setting these environment variables:

```env
LOG_LEVEL=DEBUG
LOG_DEBUG_ENABLED=true
LOG_TO_FILE=true
LOG_FILE_PATH=logs/debug.log
```

### Performance Profiling

For performance issues, consider:

1. **Memory Profiling**: Use tools like `memory_profiler`
2. **CPU Profiling**: Use `cProfile` for performance bottlenecks
3. **Async Profiling**: Monitor event loop performance
4. **Storage Profiling**: Measure file I/O performance

### Network Troubleshooting

**Check Connectivity**:
```bash
# Test internet connectivity
ping google.com

# Check specific AI provider endpoints
curl -I https://api.openai.com/v1/models
curl -I https://models.inference.ai.azure.com
```

**Proxy Issues**:
If behind a corporate proxy, configure environment variables:
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Container Troubleshooting

If using Docker:

**Check Container Status**:
```bash
docker ps
docker logs <container-id>
```

**Debug Container Environment**:
```bash
docker exec -it <container-id> /bin/bash
env | grep -E "(OPENAI|AI_PROVIDER|LOG_LEVEL)"
```

## Getting Community Support

1. **GitHub Issues**: Report bugs or request features on the project repository
2. **Documentation**: Check the comprehensive documentation in the `docs/` folder
3. **Configuration Guide**: Review the [Configuration Documentation](configuration.md)
4. **Storage Guide**: Check the [Storage System Documentation](storage-system.md)

## Prevention Tips

### Best Practices

1. **Regular Updates**: Keep dependencies up to date
2. **Environment Isolation**: Use virtual environments for clean installations
3. **Configuration Validation**: Validate settings before deployment
4. **Monitoring**: Implement logging and monitoring for production use
5. **Backup**: Regular backup of configuration and data files

### Maintenance Tasks

1. **Log Rotation**: Implement log file rotation to prevent disk space issues
2. **Cache Cleanup**: Periodically clean old cached data
3. **Dependency Audits**: Regular security audits of dependencies
4. **Performance Monitoring**: Monitor application performance metrics
5. **Configuration Reviews**: Periodic review of configuration settings