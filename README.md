# NFL Transactions Automation Pipeline
## 🏈 Automated NFL Transaction Scraping → Google Sheets → Airtable

**Revolutionary automated system that tracks NFL transactions in real-time and populates your databases automatically.**

---

## 🚀 **SYSTEM ARCHITECTURE**
ESPN API → Python Scraper → Google Sheets → Zapier → Airtable
↓           ↓              ↓           ↓        ↓
Daily Data → Processing → Structured Data → Sync → Final DB

## 🎯 **FEATURES**

- **✅ Daily Automated Scraping** - ESPN API integration runs daily at 9 AM EST
- **✅ Google Sheets Integration** - Automatic population of transaction data
- **✅ Airtable Sync** - Seamless data flow via Zapier
- **✅ Zero Manual Work** - Complete automation from source to final database
- **✅ Error Handling** - Robust error management and notifications
- **✅ Data Validation** - Duplicate prevention and data integrity

## 📊 **TRANSACTION TYPES TRACKED**

- **Trades** - Player trades between teams
- **Signings** - Free agent signings and contract extensions
- **Releases** - Player releases and cuts
- **Waivers** - Waiver claims and designations
- **Practice Squad** - PS signings and releases
- **Injured Reserve** - IR placements and activations

## 🛠️ **TECHNICAL STACK**

- **Data Source:** ESPN NFL Transactions API (Free)
- **Processing:** Python 3.9+
- **Storage:** Google Sheets
- **Automation:** GitHub Actions
- **Integration:** Zapier
- **Final Database:** Airtable

## 🚀 **QUICK START**

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/nfl-transactions-automation.git
   cd nfl-transactions-automation

Install Dependencies
bashpip install -r requirements.txt

Configure Credentials
bashcp .env.example .env
# Add your Google Sheets credentials

Run Manual Test
bashpython src/transaction_scraper.py


📋 SETUP GUIDE
Google Sheets API Setup

Create Google Cloud Project
Enable Google Sheets API
Generate Service Account Credentials
Share your sheet with the service account email

GitHub Actions Setup

Add GOOGLE_CREDENTIALS secret (base64 encoded)
Add SHEET_ID secret
Configure workflow schedule

Zapier Integration

Connect Google Sheets to Zapier
Set up Airtable integration
Configure field mappings
Test automation flow

🔄 AUTOMATION SCHEDULE

Daily Scraping: 9:00 AM EST
Sheet Updates: Real-time
Airtable Sync: Every 15 minutes (via Zapier)
Error Notifications: Immediate

📈 DATA STRUCTURE
FieldTypeDescriptiondateDateTransaction datetypeStringTransaction typeteamStringTeam nameplayerStringPlayer namedescriptionStringFull transaction descriptiontransaction_idStringUnique identifierscraped_atDateTimeWhen data was collected
🏆 BENEFITS

⏰ Time Savings - No manual transaction tracking
📊 Data Consistency - Standardized format across platforms
🔄 Real-time Updates - Always current information
📱 Accessibility - Available in Google Sheets and Airtable
🔒 Reliable - Automated error handling and recovery

📞 SUPPORT
For questions or issues:

Create GitHub issue
Check troubleshooting guide
Review API documentation


🏈 Never manually track NFL transactions again! This system runs automatically and keeps your databases perfectly updated.

**Commit message:** `Add comprehensive README for NFL transaction automation pipeline`

### **Step 3: Create Python Scripts Structure**

**File 2: Requirements File**
- Click "Add file" → "Create new file"
- **Filename:** `requirements.txt`
- **Content:**

```txt
requests>=2.31.0
pandas>=2.0.0
gspread>=5.10.0
google-auth>=2.22.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
python-dotenv>=1.0.0
schedule>=1.2.0
retry>=0.9.2
Commit message: Add Python dependencies for NFL transaction scraper
File 3: Environment Template

Click "Add file" → "Create new file"
Filename: .env.example
Content:

env# Google Sheets Configuration
GOOGLE_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# ESPN API Configuration
ESPN_API_BASE_URL=https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/transactions
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Automation Configuration
SCRAPE_SCHEDULE=09:00
TIMEZONE=America/New_York
MAX_RETRIES=3
BATCH_SIZE=100

# Notification Configuration (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
EMAIL_NOTIFICATIONS=false
Commit message: Add environment configuration template
Step 4: Create Core Python Scripts
File 4: Main Transaction Scraper

Click "Add file" → "Create new file"
Filename: src/transaction_scraper.py
Content:

python"""
NFL Transaction Scraper
Automated scraping of NFL transactions from ESPN API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import logging
from typing import List, Dict, Optional
from retry import retry
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NFLTransactionScraper:
    """
    ESPN NFL Transaction Scraper
    Fetches daily NFL transactions and processes them for Google Sheets
    """
    
    def __init__(self):
        self.base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/transactions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    @retry(tries=3, delay=2, backoff=2)
    def fetch_transactions(self, date: Optional[str] = None) -> Dict:
        """
        Fetch transactions from ESPN API
        
        Args:
            date: Date in YYYY-MM-DD format, defaults to today
            
        Returns:
            Dictionary containing transaction data
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"🏈 Fetching NFL transactions for {date}")
        
        params = {
            'limit': 100,
            'dates': date
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Successfully fetched {len(data.get('items', []))} transactions")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching transactions: {e}")
            raise
    
    def parse_transactions(self, data: Dict) -> pd.DataFrame:
        """
        Parse ESPN API response into structured DataFrame
        
        Args:
            data: Raw API response data
            
        Returns:
            Pandas DataFrame with processed transaction data
        """
        logger.info("📊 Parsing transaction data")
        
        transactions = []
        
        for item in data.get('items', []):
            try:
                # Extract transaction details
                transaction = {
                    'date': item.get('date', ''),
                    'type': item.get('type', {}).get('displayName', 'Unknown'),
                    'team': item.get('team', {}).get('displayName', 'Unknown'),
                    'player': item.get('player', {}).get('displayName', 'Unknown'),
                    'description': item.get('description', ''),
                    'transaction_id': item.get('id', ''),
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Clean and validate data
                transaction = self.clean_transaction_data(transaction)
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing transaction: {e}")
                continue
        
        df = pd.DataFrame(transactions)
        logger.info(f"✅ Parsed {len(df)} transactions successfully")
        return df
    
    def clean_transaction_data(self, transaction: Dict) -> Dict:
        """
        Clean and validate transaction data
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Cleaned transaction dictionary
        """
        # Remove empty strings and None values
        for key, value in transaction.items():
            if value is None or value == '':
                transaction[key] = 'Unknown'
        
        # Format date
        if transaction['date']:
            try:
                # Parse and reformat date
                date_obj = datetime.fromisoformat(transaction['date'].replace('Z', '+00:00'))
                transaction['date'] = date_obj.strftime('%Y-%m-%d')
            except:
                transaction['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return transaction
    
    def get_daily_transactions(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Get and process daily NFL transactions
        
        Args:
            date: Date in YYYY-MM-DD format, defaults to today
            
        Returns:
            DataFrame with processed transactions
        """
        logger.info("🚀 Starting daily transaction collection")
        
        try:
            # Fetch raw data
            raw_data = self.fetch_transactions(date)
            
            # Parse and clean data
            df = self.parse_transactions(raw_data)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['transaction_id'], keep='first')
            
            # Sort by date
            df = df.sort_values('date')
            
            logger.info(f"🏆 Successfully processed {len(df)} unique transactions")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error in daily transaction collection: {e}")
            raise
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Save transactions to CSV file
        
        Args:
            df: DataFrame with transaction data
            filename: Optional filename, defaults to date-based name
            
        Returns:
            Filename of saved file
        """
        if not filename:
            filename = f"data/nfl_transactions_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"💾 Saved {len(df)} transactions to {filename}")
        return filename


def main():
    """Main execution function"""
    logger.info("🏈 NFL Transaction Scraper Starting")
    
    try:
        scraper = NFLTransactionScraper()
        
        # Get today's transactions
        transactions_df = scraper.get_daily_transactions()
        
        if not transactions_df.empty:
            # Save to CSV
            filename = scraper.save_to_csv(transactions_df)
            
            # Print summary
            print(f"\n🏆 NFL TRANSACTION SUMMARY")
            print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"📊 Total Transactions: {len(transactions_df)}")
            print(f"💾 Saved to: {filename}")
            
            # Show transaction types
            type_counts = transactions_df['type'].value_counts()
            print(f"\n📋 Transaction Types:")
            for trans_type, count in type_counts.items():
                print(f"  • {trans_type}: {count}")
            
        else:
            logger.info("📭 No transactions found for today")
            
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        raise

if __name__ == "__main__":
    main()
Commit message: Add NFL transaction scraper with ESPN API integration
Step 5: Create Google Sheets Integration
File 5: Google Sheets Updater

Click "Add file" → "Create new file"
Filename: src/google_sheets_updater.py
Content:

python"""
Google Sheets Updater for NFL Transactions
Automatically updates Google Sheets with scraped transaction data
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import os
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleSheetsUpdater:
    """
    Google Sheets Integration for NFL Transactions
    Handles automatic updates and data management
    """
    
    def __init__(self, credentials_path: str = None, sheet_id: str = None):
        """
        Initialize Google Sheets connection
        
        Args:
            credentials_path: Path to Google service account credentials
            sheet_id: Google Sheet ID
        """
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Get credentials and sheet ID from environment if not provided
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        
        if not self.credentials_path or not self.sheet_id:
            raise ValueError("Google credentials path and sheet ID are required")
        
        self.client = None
        self.sheet = None
        self.worksheet = None
        
        self.connect()
    
    def connect(self):
        """Establish connection to Google Sheets"""
        try:
            logger.info("🔗 Connecting to Google Sheets")
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scope
            )
            
            # Authorize client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.sheet = self.client.open_by_key(self.sheet_id)
            
            logger.info("✅ Successfully connected to Google Sheets")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            raise
    
    def setup_worksheet(self, worksheet_name: str = "NFL_Transactions"):
        """
        Set up or create worksheet with proper headers
        
        Args:
            worksheet_name: Name of the worksheet
        """
        try:
            # Try to get existing worksheet
            self.worksheet = self.sheet.worksheet(worksheet_name)
            logger.info(f"📊 Using existing worksheet: {worksheet_name}")
            
        except gspread.WorksheetNotFound:
            # Create new worksheet
            logger.info(f"📝 Creating new worksheet: {worksheet_name}")
            self.worksheet = self.sheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=10
            )
            
            # Add headers
            headers = [
                'Date', 'Type', 'Team', 'Player', 'Description', 
                'Transaction ID', 'Scraped At'
            ]
            self.worksheet.append_row(headers)
            
            # Format headers
            self.worksheet.format('A1:G1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8}
            })
            
            logger.info("✅ Worksheet created and formatted")
    
    def get_existing_transaction_ids(self) -> List[str]:
        """
        Get list of existing transaction IDs to prevent duplicates
        
        Returns:
            List of existing transaction IDs
        """
        try:
            # Get all values from transaction ID column (column F)
            values = self.worksheet.col_values(6)  # Column F (Transaction ID)
            
            # Remove header and empty values
            transaction_ids = [val for val in values[1:] if val]
            
            logger.info(f"📋 Found {len(transaction_ids)} existing transactions")
            return transaction_ids
            
        except Exception as e:
            logger.warning(f"⚠️ Could not retrieve existing transaction IDs: {e}")
            return []
    
    def filter_new_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out transactions that already exist in the sheet
        
        Args:
            df: DataFrame with new transactions
            
        Returns:
            DataFrame with only new transactions
        """
        existing_ids = self.get_existing_transaction_ids()
        
        if not existing_ids:
            logger.info("📝 No existing transactions, all data is new")
            return df
        
        # Filter out existing transactions
        new_df = df[~df['transaction_id'].isin(existing_ids)]
        
        logger.info(f"🔍 Filtered {len(df) - len(new_df)} duplicate transactions")
        logger.info(f"📊 {len(new_df)} new transactions to add")
        
        return new_df
    
    def append_transactions(self, df: pd.DataFrame) -> int:
        """
        Append new transactions to Google Sheet
        
        Args:
            df: DataFrame with transaction data
            
        Returns:
            Number of transactions added
        """
        if df.empty:
            logger.info("📭 No new transactions to add")
            return 0
        
        try:
            # Prepare data for Google Sheets
            data = []
            for _, row in df.iterrows():
                data.append([
                    row['date'],
                    row['type'],
                    row['team'],
                    row['player'],
                    row['description'],
                    row['transaction_id'],
                    row['scraped_at']
                ])
            
            # Append to worksheet
            self.worksheet.append_rows(data, value_input_option='USER_ENTERED')
            
            logger.info(f"✅ Successfully added {len(data)} transactions to Google Sheets")
            return len(data)
            
        except Exception as e:
            logger.error(f"❌ Error appending transactions: {e}")
            raise
    
    def update_metadata(self):
        """Update metadata sheet with last update info"""
        try:
            # Try to get or create metadata worksheet
            try:
                meta_sheet = self.sheet.worksheet("Metadata")
            except gspread.WorksheetNotFound:
                meta_sheet = self.sheet.add_worksheet(title="Metadata", rows=10, cols=2)
                meta_sheet.append_row(["Field", "Value"])
            
            # Update last run time
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Clear existing metadata and add new
            meta_sheet.clear()
            meta_sheet.append_rows([
                ["Field", "Value"],
                ["Last Updated", current_time],
                ["Data Source", "ESPN NFL Transactions API"],
                ["Automation", "GitHub Actions"],
                ["Status", "Active"]
            ])
            
            logger.info("📊 Updated metadata worksheet")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not update metadata: {e}")
    
    def process_daily_update(self, df: pd.DataFrame, worksheet_name: str = "NFL_Transactions") -> Dict:
        """
        Complete daily update process
        
        Args:
            df: DataFrame with transaction data
            worksheet_name: Name of the worksheet
            
        Returns:
            Dictionary with update results
        """
        logger.info("🚀 Starting daily Google Sheets update")
        
        try:
            # Setup worksheet
            self.setup_worksheet(worksheet_name)
            
            # Filter new transactions
            new_df = self.filter_new_transactions(df)
            
            # Add new transactions
            added_count = self.append_transactions(new_df)
            
            # Update metadata
            self.update_metadata()
            
            result = {
                'success': True,
                'total_transactions': len(df),
                'new_transactions': added_count,
                'duplicate_transactions': len(df) - added_count,
                'worksheet_name': worksheet_name,
                'updated_at': datetime.now().isoformat()
            }
            
            logger.info(f"🏆 Daily update completed successfully: {added_count} new transactions added")
            return result
            
        except Exception as e:
            logger.error(f"❌ Daily update failed: {e}")
            raise


def main():
    """Main execution function for testing"""
    logger.info("📊 Google Sheets Updater Test")
    
    # This would normally be called from the main scraper
    # For testing, you can create sample data
    sample_data = pd.DataFrame([
        {
            'date': '2024-01-01',
            'type': 'Signing',
            'team': 'Philadelphia Eagles',
            'player': 'Test Player',
            'description': 'Test transaction',
            'transaction_id': 'test_001',
            'scraped_at': datetime.now().isoformat()
        }
    ])
    
    try:
        updater = GoogleSheetsUpdater()
        result = updater.process_daily_update(sample_data)
        print(f"✅ Test completed: {result}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
