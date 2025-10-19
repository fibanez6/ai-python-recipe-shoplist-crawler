# Mock AI Responses

This folder contains example AI responses for development and testing purposes.

## 📁 Structure

- `recipe_analysis/` - Recipe parsing and ingredient extraction responses
- `shopping_optimization/` - Store optimization and price comparison responses
- `bill_generation/` - Shopping list and bill generation responses

## 🔧 Usage

Set `USE_MOCK_AI_RESPONSES=true` in your `.env` file to use these mock responses instead of making real AI API calls.

## ✅ Benefits

- **Faster Development** - No API call delays
- **Cost Savings** - No API usage charges during development
- **Consistent Testing** - Predictable responses for tests
- **Offline Development** - Work without internet connection
- **Demo Ready** - Reliable responses for demonstrations

## 📝 File Format

Each mock response file contains:
- `input` - The prompt that would be sent to the AI
- `output` - The expected AI response
- `metadata` - Additional information about the response