"""
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
