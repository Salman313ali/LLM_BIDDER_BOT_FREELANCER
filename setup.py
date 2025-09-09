#!/usr/bin/env python3
"""
Setup script for Freelancer Bot
"""
import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
    except FileNotFoundError:
        pass
    print("❌ Node.js is not installed or not in PATH")
    return False

def setup_backend():
    """Setup Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Create backend directory if it doesn't exist
    if not os.path.exists("backend"):
        os.makedirs("backend")
        print("✅ Created backend directory")
    
    return True

def setup_frontend():
    """Setup React frontend"""
    print("\n⚛️ Setting up React frontend...")
    
    # Check if frontend directory exists
    if not os.path.exists("frontend"):
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    os.chdir("frontend")
    if not run_command("npm install", "Installing Node.js dependencies"):
        os.chdir("..")
        return False
    os.chdir("..")
    
    return True

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists(".env") and os.path.exists("env.example"):
        shutil.copy("env.example", ".env")
        print("✅ Created .env file from example")
        print("⚠️  Please edit .env file with your actual API keys")
    elif os.path.exists(".env"):
        print("✅ .env file already exists")
    else:
        print("⚠️  No env.example file found, you'll need to create .env manually")

def main():
    """Main setup function"""
    print("🚀 Freelancer Bot Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node_version():
        print("⚠️  Node.js is required for the frontend. Please install it from https://nodejs.org/")
        return False
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return False
    
    # Create environment file
    create_env_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run 'python start_backend.bat' to start the backend")
    print("3. Run 'python start_frontend.bat' to start the frontend")
    print("4. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

