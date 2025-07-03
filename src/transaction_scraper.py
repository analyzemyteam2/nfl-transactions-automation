"""
Spotrac NFL Transaction Scraper
Scrapes live NFL transactions from Spotrac.com
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import re
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpotracNFLScraper:
    """
    Spotrac NFL Transaction Scraper
    Fetches live NFL transactions from Spotrac.com
    """
    
    def __init__(self):
        self.base_url = "https://www.spotrac.com/nfl/transactions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Team abbreviation mapping
        self.team_mapping = {
            'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens',
            'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears',
            'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
            'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
            'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
            'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LAC': 'Los Angeles Chargers',
            'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
            'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks', 'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders'
        }
    
    def fetch_transactions(self, days_back: int = 7) -> List[Dict]:
        """
        Fetch transactions from Spotrac
        
        Args:
            days_back: Number of days back to fetch (default 7)
            
        Returns:
            List of transaction dictionaries
        """
        logger.info(f"🏈 Fetching NFL transactions from Spotrac (last {days_back} days)")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse transactions from the page
            transactions = self.parse_spotrac_page(soup, response.text)
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_transactions = []
            
            for transaction in transactions:
                try:
                    trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                    if trans_date >= cutoff_date:
                        filtered_transactions.append(transaction)
                except:
                    # If date parsing fails, include the transaction
                    filtered_transactions.append(transaction)
            
            logger.info(f"✅ Successfully fetched {len(filtered_transactions)} recent transactions")
            return filtered_transactions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching transactions: {e}")
            raise
    
    def parse_spotrac_page(self, soup, html_content: str) -> List[Dict]:
        """
        Parse transactions from Spotrac page
        """
        transactions = []
        
        # Method 1: Try to find structured data
        try:
            # Look for common transaction containers
            transaction_elements = (
                soup.find_all('div', class_='transaction') or
                soup.find_all('tr') or
                soup.find_all('div', class_='row') or
                soup.find_all('li')
            )
            
            if transaction_elements:
                transactions = self.parse_structured_elements(transaction_elements)
        except Exception as e:
            logger.warning(f"Structured parsing failed: {e}")
        
        # Method 2: Fallback to text pattern matching
        if not transactions:
            transactions = self.parse_text_patterns(html_content)
        
        return transactions
    
    def parse_structured_elements(self, elements) -> List[Dict]:
        """Parse transactions from HTML elements"""
        transactions = []
        
        for element in elements:
            text = element.get_text().strip()
            if self.is_transaction_text(text):
                parsed = self.parse_transaction_text(text)
                if parsed:
                    transactions.append(parsed)
        
        return transactions
    
    def parse_text_patterns(self, html_content: str) -> List[Dict]:
        """
        Parse transactions using text pattern matching
        Based on the format you showed from Spotrac
        """
        transactions = []
        lines = html_content.split('\n')
        
        current_player = None
        current_position = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Pattern 1: Player Name (Position)
            player_match = re.search(r'^([^(]+)\s*\(([^)]+)\)\s*$', line)
            if player_match:
                current_player = player_match.group(1).strip()
                current_position = player_match.group(2).strip()
                continue
            
            # Pattern 2: Date - Transaction details
            if current_player and re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d+\s*-', line):
                parsed = self.parse_transaction_line(line, current_player, current_position)
                if parsed:
                    transactions.append(parsed)
                current_player = None
                current_position = None
        
        return transactions
    
    def is_transaction_text(self, text: str) -> bool:
        """Check if text contains transaction information"""
        transaction_keywords = [
            'signed', 'released', 'traded', 'waived', 'claimed', 
            'contract', 'extension', 'suspended', 'retired'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in transaction_keywords)
    
    def parse_transaction_text(self, text: str) -> Optional[Dict]:
        """Parse a single transaction text"""
        try:
            # Extract player and position
            player_match = re.search(r'^([^(]+)\s*\(([^)]+)\)', text)
            if not player_match:
                return None
            
            player = player_match.group(1).strip()
            position = player_match.group(2).strip()
            
            # Find the transaction line (everything after position)
            transaction_part = text[player_match.end():].strip()
            
            return self.parse_transaction_line(transaction_part, player, position)
            
        except Exception as e:
            logger.warning(f"Error parsing transaction text: {e}")
            return None
    
    def parse_transaction_line(self, line: str, player: str = None, position: str = None) -> Optional[Dict]:
        """
        Parse transaction line like:
        "Jul 03, 2025 - Signed a 3 year contract extension through 2028 with Pittsburgh (PIT)"
        """
        try:
            # Extract date
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+),\s+(\d+)', line)
            if not date_match:
                return None
            
            month_str, day, year = date_match.groups()
            month_num = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }[month_str]
            
            date_str = f"{year}-{month_num:02d}-{int(day):02d}"
            
            # Extract transaction details (everything after the dash)
            dash_index = line.find(' - ')
            if dash_index == -1:
                return None
            
            description = line[dash_index + 3:].strip()
            
            # Extract team
            team_match = re.search(r'with\s+([^(]+)\s*\(([^)]+)\)', description) or re.search(r'by\s+([^(]+)\s*\(([^)]+)\)', description)
            team_full = team_match.group(1).strip() if team_match else "Unknown"
            team_abbr = team_match.group(2).strip() if team_match else "UNK"
            
            # Map team abbreviation to full name
            team = self.team_mapping.get(team_abbr, team_full)
            
            # Determine transaction type
            transaction_type = self.classify_transaction(description)
            
            # Generate unique ID
            transaction_id = f"SPOTRAC_{date_str}_{player.replace(' ', '_')}_{hash(description) % 10000:04d}"
            
            return {
                'date': date_str,
                'type': transaction_type,
                'team': team,
                'player': player or "Unknown Player",
                'position': position or "",
                'description': description,
                'transaction_id': transaction_id,
                'scraped_at': datetime.now().isoformat(),
                'source': 'Spotrac'
            }
            
        except Exception as e:
            logger.warning(f"Error parsing transaction line: {e}")
            return None
    
    def classify_transaction(self, description: str) -> str:
        """Classify transaction type based on description"""
        desc_lower = description.lower()
        
        if 'signed' in desc_lower and 'extension' in desc_lower:
            return 'Contract Extension'
        elif 'signed' in desc_lower:
            return 'Signing'
        elif 'traded' in desc_lower:
            return 'Trade'
        elif 'released' in desc_lower:
            return 'Release'
        elif 'waived' in desc_lower:
            return 'Waiver'
        elif 'claimed' in desc_lower:
            return 'Waiver Claim'
        elif 'suspended' in desc_lower:
            return 'Suspension'
        elif 'retired' in desc_lower:
            return 'Retirement'
        else:
            return 'Other'
    
    def get_daily_transactions(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Get transactions for a specific date or recent transactions
        
        Args:
            date: Date in YYYY-MM-DD format, defaults to recent transactions
            
        Returns:
            DataFrame with processed transactions
        """
        logger.info("🚀 Starting Spotrac NFL transaction collection")
        
        try:
            # Fetch raw transaction data
            raw_transactions = self.fetch_transactions(days_back=7)
            
            # Convert to DataFrame
            if raw_transactions:
                df = pd.DataFrame(raw_transactions)
                
                # Remove duplicates
                df = df.drop_duplicates(subset=['transaction_id'], keep='first')
                
                # Sort by date (newest first)
                df = df.sort_values('date', ascending=False)
                
                logger.info(f"🏆 Successfully processed {len(df)} unique transactions")
                return df
            else:
                # Return empty DataFrame with correct columns
                return pd.DataFrame(columns=[
                    'date', 'type', 'team', 'player', 'position', 
                    'description', 'transaction_id', 'scraped_at', 'source'
                ])
            
        except Exception as e:
            logger.error(f"❌ Error in transaction collection: {e}")
            raise
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save transactions to CSV file"""
        if not filename:
            filename = f"data/spotrac_nfl_transactions_{datetime.now().strftime('%Y-%m-%d')}.csv"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"💾 Saved {len(df)} transactions to {filename}")
        return filename


# Alias for compatibility with existing code
NFLTransactionScraper = SpotracNFLScraper


def main():
    """Test the scraper"""
    logger.info("🏈 Testing Spotrac NFL Transaction Scraper")
    
    try:
        scraper = SpotracNFLScraper()
        
        # Get recent transactions
        transactions_df = scraper.get_daily_transactions()
        
        if not transactions_df.empty:
            # Save to CSV
            filename = scraper.save_to_csv(transactions_df)
            
            # Print summary
            print(f"\n🏆 SPOTRAC NFL TRANSACTION SUMMARY")
            print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"📊 Total Transactions: {len(transactions_df)}")
            print(f"💾 Saved to: {filename}")
            
            # Show transaction types
            if 'type' in transactions_df.columns:
                type_counts = transactions_df['type'].value_counts()
                print(f"\n📋 Transaction Types:")
                for trans_type, count in type_counts.items():
                    print(f"  • {trans_type}: {count}")
            
            # Show recent transactions
            print(f"\n📊 Recent Transactions:")
            for i, row in transactions_df.head(5).iterrows():
                print(f"  • {row['type']}: {row['team']} - {row['player']}")
            
        else:
            logger.info("📭 No transactions found")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
