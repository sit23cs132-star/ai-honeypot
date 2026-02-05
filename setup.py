"""Setup script for deployment."""
import subprocess
import sys
import os


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python version: {sys.version}")


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("\n⚠️  .env file not found")
        print("Creating .env from .env.example...")
        
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as source:
                content = source.read()
            
            with open(".env", "w") as target:
                target.write(content)
            
            print("✓ .env file created")
            print("\n⚠️  IMPORTANT: Edit .env file and add your API keys!")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    else:
        print("✓ .env file exists")


def verify_configuration():
    """Verify that required configurations are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🔍 Verifying configuration...")
    
    warnings = []
    
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your-secret-api-key-here":
        warnings.append("API_KEY is not set or using default value")
    
    ai_provider = os.getenv("AI_PROVIDER", "openai")
    
    if ai_provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or openai_key == "your-openai-api-key":
            warnings.append("OPENAI_API_KEY is not set")
    
    elif ai_provider == "anthropic":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key or anthropic_key == "your-anthropic-api-key":
            warnings.append("ANTHROPIC_API_KEY is not set")
    
    if warnings:
        print("\n⚠️  Configuration warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print("\nPlease update your .env file with proper values")
    else:
        print("✓ Configuration looks good")


def main():
    """Main setup function."""
    print("=" * 60)
    print("AGENTIC HONEY-POT SETUP")
    print("=" * 60)
    
    check_python_version()
    install_dependencies()
    check_env_file()
    verify_configuration()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py")
    print("3. Test: python test_client.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
