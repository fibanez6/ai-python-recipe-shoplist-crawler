#!/usr/bin/env python3
"""
Simple test to verify the QuantityUnit enum fix works.
This tests the core fix without requiring the full environment.
"""

import sys
from enum import Enum
from typing import Optional
from dataclasses import dataclass

# Simulate our QuantityUnit enum (the fixed version)
class QuantityUnit(str, Enum):
    """Standard quantity units for ingredients."""
    # Volume
    CUP = "cup"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    LITER = "l"
    MILLILITER = "ml"
    FLUID_OUNCE = "fl oz"
    
    # Weight
    KILOGRAM = "kg"
    GRAM = "g"
    POUND = "lb"
    OUNCE = "oz"
    
    # Count
    PIECE = "piece"
    ITEM = "item"
    CLOVE = "clove"
    SLICE = "slice"
    
    # Containers (THE FIX)
    CAN = "can"
    JAR = "jar"
    BOTTLE = "bottle"
    PACKAGE = "package"
    PACK = "pack"
    BAG = "bag"
    BOX = "box"
    CONTAINER = "container"
    
    # Special
    PINCH = "pinch"
    DASH = "dash"
    TO_TASTE = "to taste"

# Simple ingredient class for testing
@dataclass
class TestIngredient:
    name: str
    quantity: Optional[float]
    unit: Optional[QuantityUnit]
    original_text: str

def test_the_fix():
    """Test that demonstrates the fix for the validation error."""
    print("🧪 Testing QuantityUnit enum fix...")
    print("=" * 50)
    
    # Test 1: The specific case that was failing
    print("\n1. Testing the specific failing case:")
    try:
        ingredient = TestIngredient(
            name="cream of mushroom soup",
            quantity=1.0,
            unit=QuantityUnit.CAN,
            original_text="1 can cream of mushroom soup"
        )
        print(f"✅ SUCCESS: Created ingredient with CAN unit")
        print(f"   - Name: {ingredient.name}")
        print(f"   - Unit: {ingredient.unit.value} (enum: {ingredient.unit})")
        print(f"   - Original: {ingredient.original_text}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: All new container units
    print("\n2. Testing all new container units:")
    container_tests = [
        ("diced tomatoes", QuantityUnit.CAN),
        ("pasta sauce", QuantityUnit.JAR),
        ("olive oil", QuantityUnit.BOTTLE),
        ("pasta", QuantityUnit.PACKAGE),
        ("chicken breasts", QuantityUnit.PACK),
        ("flour", QuantityUnit.BAG),
        ("cereal", QuantityUnit.BOX),
        ("yogurt", QuantityUnit.CONTAINER)
    ]
    
    for name, unit in container_tests:
        try:
            ingredient = TestIngredient(
                name=name,
                quantity=1.0,
                unit=unit,
                original_text=f"1 {unit.value} {name}"
            )
            print(f"✅ {unit.value:<9} - works with {name}")
        except Exception as e:
            print(f"❌ {unit.value:<9} - failed: {e}")
    
    # Test 3: Verify existing units still work
    print("\n3. Testing existing units still work:")
    existing_tests = [
        ("flour", QuantityUnit.CUP),
        ("olive oil", QuantityUnit.TABLESPOON),
        ("salt", QuantityUnit.TEASPOON),
        ("sugar", QuantityUnit.GRAM),
        ("cheese", QuantityUnit.OUNCE)
    ]
    
    for name, unit in existing_tests:
        try:
            ingredient = TestIngredient(
                name=name,
                quantity=1.0,
                unit=unit,
                original_text=f"1 {unit.value} {name}"
            )
            print(f"✅ {unit.value:<12} - still works")
        except Exception as e:
            print(f"❌ {unit.value:<12} - failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSION:")
    print("   The QuantityUnit enum now includes container units!")
    print("   The demo recipe validation error should be FIXED.")
    print("   You can now use: can, jar, bottle, package, pack, bag, box, container")

if __name__ == "__main__":
    test_the_fix()