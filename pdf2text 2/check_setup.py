"""
Quick Start Guide for PDF2Text AI Application

This script helps you get started quickly by checking the setup
and providing step-by-step instructions.
"""
import os
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("⚠ Warning: Python 3.11+ is recommended")
        return False
    return True


def check_dependencies():
    """Check if dependencies are installed"""
    required_packages = [
        'pdfplumber',
        'streamlit',
        'requests',
        'docx',
        'loguru',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').split('.')[0])
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages


def check_env_file():
    """Check if .env file exists and is configured"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("✗ .env file not found")
        print("  Creating from .env.example...")
        
        example_path = Path('.env.example')
        if example_path.exists():
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ Created .env file")
            print("⚠ Please edit .env and add your DeepSeek API key")
            return False
        else:
            print("✗ .env.example not found")
            return False
    
    print("✓ .env file exists")
    
    # Check if API key is configured
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        if not api_key or api_key == 'your_deepseek_api_key_here':
            print("⚠ DeepSeek API key not configured in .env")
            return False
        else:
            print("✓ DeepSeek API key configured")
            return True
    except Exception as e:
        print(f"⚠ Error reading .env: {e}")
        return False


def check_directories():
    """Check if required directories exist"""
    directories = ['logs', 'outputs', 'temp']
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created {dir_name}/ directory")
        else:
            print(f"✓ {dir_name}/ directory exists")
    
    return True


def print_usage_instructions():
    """Print usage instructions"""
    print_header("How to Use PDF2Text AI")
    
    print("Step 1: Configure API Key")
    print("  - Edit .env file")
    print("  - Add your DeepSeek API key")
    print("  - Get API key from: https://platform.deepseek.com")
    print()
    
    print("Step 2: Start the Application")
    print("  Windows: run.bat")
    print("  Linux/Mac: ./run.sh")
    print("  Or directly: streamlit run app.py")
    print()
    
    print("Step 3: Use the Web Interface")
    print("  - Open http://localhost:8501 in your browser")
    print("  - Upload a PDF file")
    print("  - Configure processing options")
    print("  - Click 'Process PDF'")
    print("  - Preview and export results")
    print()
    
    print("Docker Deployment:")
    print("  docker build -t pdf2text-ai .")
    print("  docker run -p 8501:8501 -e DEEPSEEK_API_KEY=your_key pdf2text-ai")
    print()


def main():
    """Main check function"""
    print_header("PDF2Text AI - Quick Start Check")
    
    # Check Python version
    print("[1/4] Checking Python version...")
    python_ok = check_python_version()
    
    # Check dependencies
    print("\n[2/4] Checking dependencies...")
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
    
    # Check environment file
    print("\n[3/4] Checking configuration...")
    env_ok = check_env_file()
    
    # Check directories
    print("\n[4/4] Checking directories...")
    dirs_ok = check_directories()
    
    # Summary
    print_header("Setup Summary")
    
    if python_ok and deps_ok and env_ok and dirs_ok:
        print("✅ All checks passed! You're ready to go!")
        print("\nStart the application:")
        print("  Windows: run.bat")
        print("  Linux/Mac: ./run.sh")
        print("  Or: streamlit run app.py")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        
        if not deps_ok:
            print("\n1. Install dependencies:")
            print("   pip install -r requirements.txt")
        
        if not env_ok:
            print("\n2. Configure API key:")
            print("   Edit .env file and add your DeepSeek API key")
    
    print_usage_instructions()


if __name__ == "__main__":
    main()
