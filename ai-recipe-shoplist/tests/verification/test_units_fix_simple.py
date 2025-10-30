#!/usr/bin/env python3
"""Test script to verify QuantityUnit enum fix for container units"""

# Direct import from local models
from app.models import Ingredient, QuantityUnit

def test_container_units():
    """Test that the new container units work in validation"""
    print("Testing QuantityUnit enum with new container units...")
    
    # Test the specific unit that was causing the validation error
    print("\n1. Testing CAN unit (the one that was causing the error):")
    try:
        ingredient = Ingredient(
            name="diced tomatoes",
            quantity=1.0,
            unit=QuantityUnit.CAN,
            category="canned goods"
        )
        print(f"✅ Successfully created ingredient: {ingredient}")
        print(f"   Unit: {ingredient.unit} (value: '{ingredient.unit.value}')")
    except Exception as e:
        print(f"❌ Error creating ingredient with CAN unit: {e}")
    
    # Test all new container units
    print("\n2. Testing all new container units:")
    container_units = [
        (QuantityUnit.CAN, "crushed tomatoes"),
        (QuantityUnit.JAR, "pasta sauce"),
        (QuantityUnit.BOTTLE, "olive oil"),
        (QuantityUnit.PACKAGE, "pasta"),
        (QuantityUnit.PACK, "chicken breasts"),
        (QuantityUnit.BAG, "flour"),
        (QuantityUnit.BOX, "cereal"),
        (QuantityUnit.CONTAINER, "yogurt")
    ]
    
    for unit, item_name in container_units:
        try:
            ingredient = Ingredient(
                name=item_name,
                quantity=1.0,
                unit=unit,
                category="test"
            )
            print(f"✅ {unit.value:<9} unit works with '{item_name}'")
        except Exception as e:
            print(f"❌ {unit.value:<9} unit failed: {e}")
    
    print("\n3. Testing that original units still work:")
    original_units = [
        (QuantityUnit.CUP, "flour"),
        (QuantityUnit.TABLESPOON, "oil"),
        (QuantityUnit.TEASPOON, "salt"),
        (QuantityUnit.GRAM, "sugar"),
        (QuantityUnit.OUNCE, "cheese")
    ]
    
    for unit, item_name in original_units:
        try:
            ingredient = Ingredient(
                name=item_name,
                quantity=1.0,
                unit=unit,
                category="test"
            )
            print(f"✅ {unit.value:<12} unit still works")
        except Exception as e:
            print(f"❌ {unit.value:<12} unit failed: {e}")

if __name__ == "__main__":
    test_container_units()
    print("\n🎯 Test completed! If you see ✅ for 'can' unit, the validation error is fixed.")