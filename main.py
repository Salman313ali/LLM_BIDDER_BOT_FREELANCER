"""
Main entry point for the Freelancer Bot
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.bot import FreelancerBot
from src.config import BID_LIMIT

def main():
    """Main function to run the bot"""
    print("🤖 Starting Freelancer Bot...")
    print(f"📊 Bid Limit: {BID_LIMIT}")
    print("=" * 50)
    
    try:
        bot = FreelancerBot()
        result = bot.start()
        
        print("=" * 50)
        print("✅ Bot execution completed!")
        print(f"📈 Total bids placed: {result.get('total_bids_placed', 0)}")
        print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


