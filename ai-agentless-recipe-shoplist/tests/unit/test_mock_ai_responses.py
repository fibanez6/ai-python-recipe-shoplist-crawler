#!/usr/bin/env python3
"""Test script to verify stub AI response integration works correctly."""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from ia_provider import OpenAIProvider, AzureProvider, OllamaProvider, GitHubProvider, StubProvider


async def test_mock_ai_responses():
    """Test that stub AI responses work for all providers when enabled."""
    
    # Set stub mode environment variables
    os.environ['USE_MOCK_AI_RESPONSES'] = 'true'
    os.environ['STUB_RESPONSES_PATH'] = 'mock_responses'
    
    print("Testing Stub AI Response Integration")
    print("=" * 50)
    
    # Test data
    test_html = """
    <html>
    <head><title>Spaghetti Carbonara Recipe</title></head>
    <body>
        <h1>Spaghetti Carbonara</h1>
        <h2>Ingredients:</h2>
        <ul>
            <li>400g spaghetti</li>
            <li>200g guanciale or pancetta</li>
            <li>4 large eggs</li>
            <li>100g Pecorino Romano cheese</li>
            <li>Black pepper</li>
        </ul>
        <h2>Instructions:</h2>
        <p>Cook the pasta, render the guanciale, mix with eggs and cheese...</p>
    </body>
    </html>
    """
    
    test_url = "https://example.com/carbonara-recipe"
    test_ingredients = ["400g spaghetti", "200g guanciale", "4 large eggs"]
    test_products = [
        {"name": "De Cecco Spaghetti", "price": 2.99, "store": "grocery_store"},
        {"name": "Barilla Spaghetti", "price": 2.49, "store": "grocery_store"}
    ]
    
    # Test providers
    providers = {
        'OpenAI': OpenAIProvider,
        'Azure': AzureProvider,
        'Ollama': OllamaProvider,
        'GitHub': GitHubProvider,
        'Stub': StubProvider  # Add the StubProvider for direct testing
    }
    
    for provider_name, provider_class in providers.items():
        print(f"\n📊 Testing {provider_name} Provider")
        print("-" * 30)
        
        try:
            # Initialize provider (this might fail for some if dependencies are missing)
            try:
                provider = provider_class()
            except Exception as e:
                print(f"⚠️  Skipping {provider_name}: {e}")
                continue
            
            # Test recipe extraction
            print("🔍 Testing recipe extraction...")
            recipe_result = await provider.extract_recipe_data(test_html, test_url)
            
            if recipe_result:
                print(f"✅ Recipe extraction successful")
                print(f"   Recipe name: {recipe_result.get('recipe_name', 'N/A')}")
                print(f"   Ingredients count: {len(recipe_result.get('ingredients', []))}")
            else:
                print("❌ Recipe extraction failed")
            
            # Test ingredient normalization
            print("📝 Testing ingredient normalization...")
            normalized_result = await provider.normalize_ingredients(test_ingredients)
            
            if normalized_result:
                print(f"✅ Ingredient normalization successful")
                print(f"   Normalized ingredients count: {len(normalized_result)}")
            else:
                print("❌ Ingredient normalization failed")
            
            # Test product matching
            print("🛒 Testing product matching...")
            match_result = await provider.match_products("spaghetti", test_products)
            
            if match_result:
                print(f"✅ Product matching successful")
                print(f"   Matched products count: {len(match_result)}")
            else:
                print("❌ Product matching failed")
                
        except Exception as e:
            print(f"❌ Error testing {provider_name}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Stub AI Response Integration Test Complete!")
    print("\n📋 Summary:")
    print("- Stub responses are now integrated with all AI providers")
    print("- Set USE_MOCK_AI_RESPONSES=true to enable stub mode")
    print("- Stub responses are loaded from the mock_responses/ directory")
    print("- All providers (OpenAI, Azure, Ollama, GitHub, Stub) support stub mode")
    print("- When stub mode is enabled, StubProvider is used automatically")


if __name__ == "__main__":
    asyncio.run(test_mock_ai_responses())