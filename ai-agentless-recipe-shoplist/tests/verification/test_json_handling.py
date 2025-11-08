#!/usr/bin/env python3
"""Test script to verify improved JSON error handling."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

def test_json_error_handling():
    """Test that JSON error handling works correctly."""
    print("🔍 Testing JSON Error Handling")
    print("=" * 40)
    
    try:
        from utils.ai_helpers import safe_json_parse
        
        # Test cases that should trigger error handling
        test_cases = [
            ("Internal Server Error", "Server error message"),
            ("HTTP 500 Error", "HTTP error message"),
            ('{"incomplete": json', "Malformed JSON"),
            ("", "Empty response"),
            ("Not JSON at all", "Non-JSON text"),
            ("Error: Something went wrong", "Error prefix"),
            ("Exception occurred", "Exception message"),
        ]
        
        print("📋 Testing error cases...")
        for test_input, description in test_cases:
            result = safe_json_parse(test_input, fallback={"error": "fallback_used"})
            if result == {"error": "fallback_used"}:
                print(f"✅ {description}: Correctly used fallback")
            else:
                print(f"❌ {description}: Unexpected result: {result}")
        
        # Test valid JSON cases
        print("\n📋 Testing valid JSON cases...")
        valid_cases = [
            ('{"valid": "json"}', "Simple JSON object"),
            ('[1, 2, 3]', "JSON array"),
            ('```json\n{"wrapped": "json"}\n```', "Markdown-wrapped JSON"),
        ]
        
        for test_input, description in valid_cases:
            result = safe_json_parse(test_input, fallback={"error": "fallback_used"})
            if result != {"error": "fallback_used"}:
                print(f"✅ {description}: Correctly parsed")
            else:
                print(f"❌ {description}: Unexpectedly used fallback")
        
        print("\n" + "=" * 40)
        print("✅ JSON Error Handling Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_json_error_handling()
    sys.exit(0 if success else 1)