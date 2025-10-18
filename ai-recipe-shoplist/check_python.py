#!/usr/bin/env python3
"""
Python 3.11 compatibility checker for AI Recipe Shoplist Crawler
"""
import sys
import platform

def check_python_version():
    """Check if Python version meets minimum requirements"""
    required_version = (3, 11)
    current_version = sys.version_info[:2]
    
    print(f"Python Version Check")
    print(f"==================")
    print(f"Current Python: {platform.python_version()}")
    print(f"Required: >= {required_version[0]}.{required_version[1]}")
    
    if current_version >= required_version:
        print("✅ Python version is compatible!")
        return True
    else:
        print("❌ Python version is too old!")
        print(f"Please upgrade to Python {required_version[0]}.{required_version[1]} or newer")
        return False

def check_packages():
    """Check if essential packages can be imported"""
    print(f"\nPackage Compatibility Check")
    print(f"=========================")
    
    packages = [
        ('fastapi', 'FastAPI web framework'),
        ('pydantic', 'Data validation'),
        ('httpx', 'HTTP client'),
        ('beautifulsoup4', 'HTML parsing'),
        ('jinja2', 'Template engine'),
        ('reportlab', 'PDF generation'),
        ('openai', 'OpenAI API client')
    ]
    
    success_count = 0
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {package} - {description} (not installed)")
    
    print(f"\nResult: {success_count}/{len(packages)} packages available")
    return success_count == len(packages)

if __name__ == "__main__":
    print("AI Recipe Shoplist Crawler - Python 3.11 Compatibility Check")
    print("=" * 60)
    
    version_ok = check_python_version()
    packages_ok = check_packages()
    
    if version_ok and packages_ok:
        print("\n🎉 System is ready! You can run the application.")
        sys.exit(0)
    else:
        print("\n⚠️  Please fix the issues above before running the application.")
        if not version_ok:
            print("   - Upgrade Python to 3.11+")
        if not packages_ok:
            print("   - Install missing packages: pip install -r requirements-minimal.txt")
        sys.exit(1)