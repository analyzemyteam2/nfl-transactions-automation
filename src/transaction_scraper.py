"""
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
