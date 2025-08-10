#!/usr/bin/env python3
"""
Russian Roulette Game Setup Script

This script helps set up the Russian Roulette multiplayer game environment.
It handles virtual environment creation, dependency installation, and basic configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🎯 Russian Roulette Multiplayer Game Setup")
    print("=" * 60)
    print("This script will set up your development environment.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again.")
        return False

    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        print("   Please install pip and try again.")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("venv")

    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True

    try:
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_venv_python():
    """Get path to Python executable in virtual environment"""
    system = platform.system().lower()

    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """Get path to pip executable in virtual environment"""
    system = platform.system().lower()

    if system == "windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_dependencies():
    """Install project dependencies"""
    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    pip_path = get_venv_pip()

    try:
        print("📦 Installing dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"],
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file with default configuration"""
    env_file = Path(".env")

    if env_file.exists():
        print("📄 .env file already exists")
        return True

    try:
        with open(env_file, "w") as f:
            f.write("# Russian Roulette Game Configuration\n")
            f.write("# Flask Settings\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
            f.write("FLASK_HOST=0.0.0.0\n")
            f.write("FLASK_PORT=5000\n")
            f.write("\n")
            f.write("# Security (generate a secure key for production)\n")
            f.write("SECRET_KEY=dev-key-change-in-production\n")
            f.write("\n")
            f.write("# Game Settings\n")
            f.write("MAX_PLAYERS=6\n")
            f.write("MIN_PLAYERS=2\n")

        print("✅ .env file created with default settings")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def print_instructions():
    """Print post-setup instructions"""
    system = platform.system().lower()

    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print()
    print("📋 Next steps:")
    print()
    print("1. Activate the virtual environment:")

    if system == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")

    print()
    print("2. Start the game server:")
    print("   python app.py")
    print("   # OR")
    print("   python run.py")
    print()
    print("3. Open your browser and go to:")
    print("   http://localhost:5000")
    print()
    print("🎯 Game Features:")
    print("   • Real-time multiplayer (2-6 players)")
    print("   • Create and join game rooms")
    print("   • Share room IDs with friends")
    print("   • Live game state updates")
    print()
    print("📖 For more information, see README.md")
    print()
    print("🎮 Have fun and play responsibly!")
    print("=" * 60)

def run_quick_test():
    """Run a quick test to verify installation"""
    python_path = get_venv_python()

    try:
        print("🧪 Running quick installation test...")

        # Test import of main modules
        test_script = """
import flask
import flask_socketio
import secrets
import random
print("✅ All required modules imported successfully")
        """

        result = subprocess.run([str(python_path), "-c", test_script],
                              capture_output=True, text=True, check=True)

        print(result.stdout.strip())
        return True

    except subprocess.CalledProcessError as e:
        print("❌ Installation test failed")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error details: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print_header()

    # Check system requirements
    if not check_python_version():
        sys.exit(1)

    if not check_pip():
        sys.exit(1)

    print()
    print("🚀 Starting setup process...")
    print()

    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating configuration file", create_env_file),
        ("Running installation test", run_quick_test)
    ]

    for step_name, step_func in steps:
        print(f"⏳ {step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed during: {step_name}")
            print("   Please check the errors above and try again.")
            sys.exit(1)
        print()

    # Print final instructions
    print_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
