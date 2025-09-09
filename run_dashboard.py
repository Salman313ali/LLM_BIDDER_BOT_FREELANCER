"""
Script to run the complete Freelancer Bot Dashboard
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("⏹️ Backend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the React frontend"""
    print("🎨 Starting React frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("⏹️ Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main function"""
    print("🤖 Freelancer Bot Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    print("📋 Available options:")
    print("1. Run backend only (FastAPI)")
    print("2. Run frontend only (React)")
    print("3. Run both (requires two terminals)")
    print("4. Run bot directly")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        run_backend()
    elif choice == "2":
        run_frontend()
    elif choice == "3":
        print("⚠️ To run both, you'll need two terminals:")
        print("Terminal 1: python run_dashboard.py (choose option 1)")
        print("Terminal 2: python run_dashboard.py (choose option 2)")
        print("\nOr use the following commands:")
        print("Backend: cd backend && uvicorn main:app --reload")
        print("Frontend: cd frontend && npm start")
    elif choice == "4":
        print("🤖 Running bot directly...")
        subprocess.run([sys.executable, "main.py"])
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()


