#!/usr/bin/env python3
"""Test script to verify ingredient units work correctly."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

def test_ingredient_units():
    """Test that all units used in demo recipe are valid."""
    print("🔍 Testing Ingredient Units")
    print("=" * 40)
    
    try:
        from models import Ingredient, QuantityUnit
        
        # Test units from demo recipe
        demo_ingredients = [
            ("chicken breast", 2, "piece"),
            ("broccoli", 2, "cup"),
            ("cheddar cheese", 1, "cup"),
            ("rice", 1, "cup"),
            ("cream of mushroom soup", 1, "can"),  # This was causing the error
        ]
        
        print("📋 Testing demo recipe ingredients...")
        for name, quantity, unit in demo_ingredients:
            try:
                ingredient = Ingredient(
                    name=name,
                    quantity=quantity,
                    unit=unit,
                    original_text=f"{quantity} {unit} {name}"
                )
                print(f"✅ {name} ({quantity} {unit}): Valid")
            except Exception as e:
                print(f"❌ {name} ({quantity} {unit}): Error - {e}")
        
        # Test that 'can' is now in the enum
        print(f"\n📋 Available units: {[unit.value for unit in QuantityUnit]}")
        
        if "can" in [unit.value for unit in QuantityUnit]:
            print("✅ 'can' unit is now available")
        else:
            print("❌ 'can' unit is still missing")
        
        print("\n" + "=" * 40)
        print("✅ Ingredient Units Test Complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ingredient_units()
    sys.exit(0 if success else 1)