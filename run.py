#!/usr/bin/env python3
"""
NFL Transaction Automation - Quick Start Runner
Simple interface for testing and running the automation system
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import subprocess

def print_banner():
    """Print application banner"""
    print("🏈" + "=" * 58 + "🏈")
    print("   NFL TRANSACTION AUTOMATION - QUICK START RUNNER")
    print("🏈" + "=" * 58 + "🏈")
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'requests', 'pandas', 'gspread', 'google-auth', 
        'python-dotenv', 'retry'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def check_credentials():
    """Check if required credentials are configured"""
    print("\n🔐 Checking credentials...")
    
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    if not credentials_path:
        print("  ❌ GOOGLE_CREDENTIALS_PATH not set")
        print("  💡 Set in .env file or environment")
        return False
    
    if not sheet_id:
        print("  ❌ GOOGLE_SHEET_ID not set")
        print("  💡 Set in .env file or environment")
        return False
    
    if not os.path.exists(credentials_path):
        print(f"  ❌ Credentials file not found: {credentials_path}")
        print("  💡 Download from Google Cloud Console")
        return False
    
    print("  ✅ GOOGLE_CREDENTIALS_PATH set")
    print("  ✅ GOOGLE_SHEET_ID set")
    print("  ✅ Credentials file exists")
    print("✅ Credentials configured!")
    return True

def run_system_test():
    """Run system connectivity tests"""
    print("\n🧪 Running system tests...")
    
    if not check_dependencies():
        return False
    
    # Add src to path for imports
    sys.path.insert(0, 'src')
    
    try:
        # Test ESPN API
        print("\n📡 Testing ESPN API...")
        from transaction_scraper import NFLTransactionScraper
        
        scraper = NFLTransactionScraper()
        data = scraper.fetch_transactions()
        
        if 'items' in data:
            print(f"  ✅ ESPN API connected ({len(data['items'])} transactions available)")
        else:
            print("  ⚠️ ESPN API connected but no data structure found")
        
    except Exception as e:
        print(f"  ❌ ESPN API test failed: {e}")
        return False
    
    # Test Google Sheets (if credentials available)
    if check_credentials():
        try:
            print("\n📊 Testing Google Sheets...")
            from google_sheets_updater import GoogleSheetsUpdater
            
            updater = GoogleSheetsUpdater()
            updater.setup_worksheet("Quick_Start_Test")
            print("  ✅ Google Sheets connected successfully")
            
        except Exception as e:
            print(f"  ❌ Google Sheets test failed: {e}")
            return False
    
    print("\n🏆 All system tests passed!")
    return True

def run_sample_scrape():
    """Run a sample transaction scrape"""
    print("\n🏈 Running sample NFL transaction scrape...")
    
    if not check_dependencies():
        return False
    
    sys.path.insert(0, 'src')
    
    try:
        from transaction_scraper import NFLTransactionScraper
        
        scraper = NFLTransactionScraper()
        df = scraper.get_daily_transactions()
        
        if not df.empty:
            print(f"\n📊 Found {len(df)} transactions for today:")
            print("-" * 50)
            
            # Show sample transactions
            for i, row in df.head(5).iterrows():
                print(f"  • {row['type']}: {row['team']} - {row['player']}")
            
            if len(df) > 5:
                print(f"  ... and {len(df) - 5} more")
            
            # Save to CSV
            filename = scraper.save_to_csv(df)
            print(f"\n💾 Saved to: {filename}")
            
        else:
            print("📭 No transactions found for today")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample scrape failed: {e}")
        return False

def run_full_automation():
    """Run the complete automation pipeline"""
    print("\n🚀 Running full automation pipeline...")
    
    if not check_dependencies() or not check_credentials():
        return False
    
    sys.path.insert(0, 'src')
    
    try:
        from main import NFLTransactionAutomation
        
        automation = NFLTransactionAutomation()
        result = automation.run_daily_automation()
        
        if result['success']:
            print(f"\n🏆 Automation completed successfully!")
            print(f"📊 Transactions found: {result['transactions_found']}")
            print(f"💾 CSV file: {result['csv_file']}")
            
            if 'transactions_added_sheets' in result:
                print(f"📊 Added to Google Sheets: {result['transactions_added_sheets']}")
        else:
            print("❌ Automation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Full automation failed: {e}")
        return False

def run_historical_data(start_date, end_date):
    """Run historical data collection"""
    print(f"\n📚 Collecting historical data from {start_date} to {end_date}...")
    
    if not check_dependencies():
        return False
    
    sys.path.insert(0, 'src')
    
    try:
        from main import NFLTransactionAutomation
        
        automation = NFLTransactionAutomation()
        automation.run_historical_backfill(start_date, end_date)
        
        print("🏆 Historical data collection completed!")
        return True
        
    except Exception as e:
        print(f"❌ Historical data collection failed: {e}")
        return False

def setup_environment():
    """Guide user through environment setup"""
    print("\n⚙️ ENVIRONMENT SETUP GUIDE")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file")
            print("💡 Edit .env file with your actual credentials")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Check directories
    directories = ['data', 'logs', 'credentials']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    print("\n📋 NEXT STEPS:")
    print("1. 🔐 Download Google Sheets credentials from Google Cloud Console")
    print("2. 📄 Save credentials as credentials/google_credentials.json")
    print("3. ✏️ Edit .env file with your Google Sheet ID")
    print("4. 🧪 Run: python run.py --test")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='NFL Transaction Automation - Quick Start Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --test              # Test system connectivity
  python run.py --sample            # Run sample transaction scrape
  python run.py --full              # Run complete automation
  python run.py --setup             # Set up environment
  python run.py --install           # Install dependencies
  python run.py --historical 2024-01-01 2024-01-07  # Historical data
        """
    )
    
    parser.add_argument('--test', action='store_true',
                       help='Run system connectivity tests')
    parser.add_argument('--sample', action='store_true',
                       help='Run sample transaction scrape')
    parser.add_argument('--full', action='store_true',
                       help='Run complete automation pipeline')
    parser.add_argument('--setup', action='store_true',
                       help='Set up environment and directories')
    parser.add_argument('--install', action='store_true',
                       help='Install required dependencies')
    parser.add_argument('--historical', nargs=2, metavar=('START_DATE', 'END_DATE'),
                       help='Collect historical data (YYYY-MM-DD format)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Load environment variables if .env exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    success = True
    
    if args.install:
        success = install_dependencies()
    elif args.setup:
        success = setup_environment()
    elif args.test:
        success = run_system_test()
    elif args.sample:
        success = run_sample_scrape()
    elif args.full:
        success = run_full_automation()
    elif args.historical:
        start_date, end_date = args.historical
        success = run_historical_data(start_date, end_date)
    else:
        # Interactive mode
        print("🎯 QUICK START OPTIONS:")
        print("1. 📦 Install dependencies")
        print("2. ⚙️ Set up environment")
        print("3. 🧪 Test system")
        print("4. 🏈 Sample scrape")
        print("5. 🚀 Full automation")
        print("6. 📚 Historical data")
        print()
        
        try:
            choice = input("Choose an option (1-6): ").strip()
            
            if choice == '1':
                success = install_dependencies()
            elif choice == '2':
                success = setup_environment()
            elif choice == '3':
                success = run_system_test()
            elif choice == '4':
                success = run_sample_scrape()
            elif choice == '5':
                success = run_full_automation()
            elif choice == '6':
                start_date = input("Start date (YYYY-MM-DD): ").strip()
                end_date = input("End date (YYYY-MM-DD): ").strip()
                success = run_historical_data(start_date, end_date)
            else:
                print("❌ Invalid option")
                success = False
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
    
    print("\n" + "🏈" + "=" * 58 + "🏈")
    
    if success:
        print("🏆 Operation completed successfully!")
        if not any([args.test, args.sample, args.full, args.setup, args.install, args.historical]):
            print("💡 Use --help to see all available options")
    else:
        print("❌ Operation failed!")
        print("💡 Check error messages above and fix any issues")
        sys.exit(1)

if __name__ == '__main__':
    main()
