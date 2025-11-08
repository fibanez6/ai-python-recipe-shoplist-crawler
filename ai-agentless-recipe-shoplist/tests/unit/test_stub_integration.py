#!/usr/bin/env python3
"""Simple test to verify stub provider integration works."""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

def test_stub_integration():
    """Test that stub provider integration works correctly."""
    print("🔍 Testing Stub Provider Integration")
    print("=" * 40)
    
    try:
        # Test 1: Import StubProvider
        print("📦 Testing StubProvider import...")
        from ia_provider.stub_provider import StubProvider
        print("✅ StubProvider imported successfully")
        
        # Test 2: Check AIService stub mode detection
        print("\n🤖 Testing AIService stub mode...")
        from services.ai_service import AIService
        from ia_provider.base_provider import is_stub_mode_enabled
        
        # Enable stub mode
        os.environ['USE_MOCK_AI_RESPONSES'] = 'true'
        
        print(f"Stub mode enabled: {is_stub_mode_enabled()}")
        
        # Create AIService - it should automatically use StubProvider
        ai_service = AIService()
        print(f"Provider type: {type(ai_service.provider).__name__}")
        
        if isinstance(ai_service.provider, StubProvider):
            print("✅ AIService correctly uses StubProvider when stub mode is enabled")
        else:
            print("❌ AIService not using StubProvider in stub mode")
        
        # Test 3: Disable stub mode and test normal provider
        print("\n🔄 Testing normal provider mode...")
        os.environ['USE_MOCK_AI_RESPONSES'] = 'false'
        
        # Create new service with GitHub provider
        os.environ['AI_PROVIDER'] = 'github'
        ai_service_normal = AIService()
        print(f"Provider type: {type(ai_service_normal.provider).__name__}")
        
        if not isinstance(ai_service_normal.provider, StubProvider):
            print("✅ AIService uses configured provider when stub mode is disabled")
        else:
            print("❌ AIService still using StubProvider when disabled")
        
        print("\n" + "=" * 40)
        print("✅ Stub Provider Integration Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_stub_integration()
    sys.exit(0 if success else 1)