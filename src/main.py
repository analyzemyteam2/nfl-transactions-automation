"""
NFL Transaction Automation - Main Integration Script
Orchestrates daily scraping and Google Sheets updates
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Import our custom modules
from transaction_scraper import NFLTransactionScraper
from google_sheets_updater import GoogleSheetsUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nfl_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NFLTransactionAutomation:
    """
    Main automation class that orchestrates the entire process
    ESPN API → Data Processing → Google Sheets → Ready for Airtable
    """
    
    def __init__(self):
        """Initialize the automation system"""
        logger.info("🚀 Initializing NFL Transaction Automation System")
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Initialize components
        self.scraper = NFLTransactionScraper()
        self.sheets_updater = None
        
        # Initialize Google Sheets if credentials are available
        try:
            self.sheets_updater = GoogleSheetsUpdater()
            logger.info("✅ Google Sheets integration initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets not available: {e}")
            logger.info("📝 Will save to CSV only")
    
    def run_daily_automation(self, date: Optional[str] = None) -> Dict:
        """
        Run the complete daily automation process
        
        Args:
            date: Optional date in YYYY-MM-DD format, defaults to today
            
        Returns:
            Dictionary with automation results
        """
        start_time = datetime.now()
        logger.info(f"🏈 Starting daily NFL transaction automation for {date or 'today'}")
        
        results = {
            'success': False,
            'start_time': start_time.isoformat(),
            'date_processed': date or datetime.now().strftime('%Y-%m-%d'),
            'transactions_found': 0,
            'transactions_saved_csv': 0,
            'transactions_added_sheets': 0,
            'csv_file': None,
            'errors': []
        }
        
        try:
            # Step 1: Scrape transactions from ESPN API
            logger.info("📡 Step 1: Scraping transactions from ESPN API")
            transactions_df = self.scraper.get_daily_transactions(date)
            
            results['transactions_found'] = len(transactions_df)
            
            if transactions_df.empty:
                logger.info("📭 No transactions found for today")
                results['success'] = True
                return results
            
            # Step 2: Save to CSV (backup)
            logger.info("💾 Step 2: Saving transactions to CSV")
            csv_filename = self.scraper.save_to_csv(transactions_df)
            results['csv_file'] = csv_filename
            results['transactions_saved_csv'] = len(transactions_df)
            
            # Step 3: Update Google Sheets (if available)
            if self.sheets_updater:
                logger.info("📊 Step 3: Updating Google Sheets")
                sheets_result = self.sheets_updater.process_daily_update(transactions_df)
                results['transactions_added_sheets'] = sheets_result['new_transactions']
                results['duplicate_transactions'] = sheets_result['duplicate_transactions']
            else:
                logger.info("⏭️ Step 3: Skipping Google Sheets (not configured)")
            
            # Step 4: Generate summary report
            self.generate_summary_report(transactions_df, results)
            
            results['success'] = True
            results['end_time'] = datetime.now().isoformat()
            
            logger.info("🏆 Daily automation completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            results['errors'].append(str(e))
            results['end_time'] = datetime.now().isoformat()
            raise
        
        return results
    
    def generate_summary_report(self, df: pd.DataFrame, results: Dict):
        """
        Generate and log summary report
        
        Args:
            df: DataFrame with transaction data
            results: Results dictionary
        """
        logger.info("📋 Generating summary report")
        
        print(f"\n🏆 NFL TRANSACTION AUTOMATION SUMMARY")
        print(f"📅 Date: {results['date_processed']}")
        print(f"⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 Total Transactions Found: {results['transactions_found']}")
        
        if not df.empty:
            # Transaction type breakdown
            type_counts = df['type'].value_counts()
            print(f"\n📋 Transaction Types:")
            for trans_type, count in type_counts.items():
                print(f"  • {trans_type}: {count}")
            
            # Team breakdown (top 5)
            team_counts = df['team'].value_counts().head(5)
            print(f"\n🏈 Most Active Teams:")
            for team, count in team_counts.items():
                print(f"  • {team}: {count}")
        
        print(f"\n💾 CSV File: {results['csv_file']}")
        
        if self.sheets_updater:
            print(f"📊 Added to Google Sheets: {results['transactions_added_sheets']}")
            if 'duplicate_transactions' in results:
                print(f"🔄 Duplicates Filtered: {results['duplicate_transactions']}")
        
        print(f"\n✅ Automation Status: {'SUCCESS' if results['success'] else 'FAILED'}")
        print(f"🔗 Ready for Zapier → Airtable integration!")
    
    def test_system_connectivity(self) -> Dict:
        """
        Test all system components
        
        Returns:
            Dictionary with connectivity test results
        """
        logger.info("🧪 Testing system connectivity")
        
        test_results = {
            'espn_api': False,
            'google_sheets': False,
            'file_system': False,
            'overall_status': False
        }
        
        # Test ESPN API
        try:
            logger.info("🔍 Testing ESPN API connection")
            test_data = self.scraper.fetch_transactions()
            test_results['espn_api'] = True
            logger.info("✅ ESPN API connection successful")
        except Exception as e:
            logger.error(f"❌ ESPN API test failed: {e}")
        
        # Test Google Sheets
        if self.sheets_updater:
            try:
                logger.info("🔍 Testing Google Sheets connection")
                self.sheets_updater.setup_worksheet("Test_Connection")
                test_results['google_sheets'] = True
                logger.info("✅ Google Sheets connection successful")
            except Exception as e:
                logger.error(f"❌ Google Sheets test failed: {e}")
        
        # Test file system
        try:
            logger.info("🔍 Testing file system access")
            test_df = pd.DataFrame([{'test': 'data'}])
            test_file = self.scraper.save_to_csv(test_df, 'data/connectivity_test.csv')
            if os.path.exists(test_file):
                os.remove(test_file)  # Clean up
            test_results['file_system'] = True
            logger.info("✅ File system access successful")
        except Exception as e:
            logger.error(f"❌ File system test failed: {e}")
        
        # Overall status
        test_results['overall_status'] = test_results['espn_api'] and test_results['file_system']
        
        return test_results
    
    def run_historical_backfill(self, start_date: str, end_date: str):
        """
        Run backfill for historical data
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        logger.info(f"📚 Starting historical backfill from {start_date} to {end_date}")
        
        from datetime import datetime, timedelta
        
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        total_transactions = 0
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime('%Y-%m-%d')
            logger.info(f"📅 Processing {date_str}")
            
            try:
                result = self.run_daily_automation(date_str)
                total_transactions += result['transactions_found']
                
                # Small delay to be respectful to ESPN API
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Failed to process {date_str}: {e}")
            
            current_date += timedelta(days=1)
        
        logger.info(f"🏆 Historical backfill completed! Total transactions: {total_transactions}")


def main():
    """Main execution function"""
    logger.info("🏈 NFL Transaction Automation - Starting")
    
    try:
        automation = NFLTransactionAutomation()
        
        # Check if this is a test run
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'test':
                # Run connectivity tests
                results = automation.test_system_connectivity()
                print(f"\n🧪 CONNECTIVITY TEST RESULTS:")
                print(f"ESPN API: {'✅' if results['espn_api'] else '❌'}")
                print(f"Google Sheets: {'✅' if results['google_sheets'] else '❌'}")
                print(f"File System: {'✅' if results['file_system'] else '❌'}")
                print(f"Overall: {'✅ READY' if results['overall_status'] else '❌ ISSUES DETECTED'}")
                
            elif command == 'backfill' and len(sys.argv) >= 4:
                # Run historical backfill
                start_date = sys.argv[2]
                end_date = sys.argv[3]
                automation.run_historical_backfill(start_date, end_date)
                
            else:
                print("Usage:")
                print("  python main.py              # Run daily automation")
                print("  python main.py test          # Test connectivity")
                print("  python main.py backfill YYYY-MM-DD YYYY-MM-DD  # Historical data")
        else:
            # Run daily automation
            results = automation.run_daily_automation()
            
            if not results['success']:
                sys.exit(1)  # Exit with error code for GitHub Actions
                
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
