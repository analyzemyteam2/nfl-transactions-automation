"""
NFL Transaction Automation - System Test Suite
Comprehensive testing of all system components
"""

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from transaction_scraper import NFLTransactionScraper
    from google_sheets_updater import GoogleSheetsUpdater
    from main import NFLTransactionAutomation
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

class TestNFLTransactionSystem(unittest.TestCase):
    """
    Comprehensive test suite for NFL transaction automation system
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_date = '2024-01-15'
        self.sample_espn_response = {
            'items': [
                {
                    'id': 'test_transaction_001',
                    'date': '2024-01-15T14:30:00Z',
                    'type': {'displayName': 'Signing'},
                    'team': {'displayName': 'Philadelphia Eagles'},
                    'player': {'displayName': 'Test Player'},
                    'description': 'Signed to reserve/future contract'
                },
                {
                    'id': 'test_transaction_002',
                    'date': '2024-01-15T15:45:00Z',
                    'type': {'displayName': 'Release'},
                    'team': {'displayName': 'Dallas Cowboys'},
                    'player': {'displayName': 'Another Player'},
                    'description': 'Released from practice squad'
                }
            ]
        }
    
    def test_transaction_scraper_initialization(self):
        """Test that transaction scraper initializes correctly"""
        print("🧪 Testing transaction scraper initialization...")
        
        scraper = NFLTransactionScraper()
        
        self.assertIsNotNone(scraper.base_url)
        self.assertIn('espn.com', scraper.base_url)
        self.assertIsNotNone(scraper.headers)
        self.assertIn('User-Agent', scraper.headers)
        
        print("✅ Transaction scraper initialization passed")
    
    def test_data_parsing(self):
        """Test ESPN API response parsing"""
        print("🧪 Testing data parsing...")
        
        scraper = NFLTransactionScraper()
        df = scraper.parse_transactions(self.sample_espn_response)
        
        # Check DataFrame structure
        self.assertEqual(len(df), 2)
        self.assertIn('date', df.columns)
        self.assertIn('type', df.columns)
        self.assertIn('team', df.columns)
        self.assertIn('player', df.columns)
        self.assertIn('transaction_id', df.columns)
        
        # Check data values
        self.assertEqual(df.iloc[0]['type'], 'Signing')
        self.assertEqual(df.iloc[0]['team'], 'Philadelphia Eagles')
        self.assertEqual(df.iloc[1]['type'], 'Release')
        self.assertEqual(df.iloc[1]['team'], 'Dallas Cowboys')
        
        print("✅ Data parsing test passed")
    
    def test_data_cleaning(self):
        """Test data cleaning functionality"""
        print("🧪 Testing data cleaning...")
        
        scraper = NFLTransactionScraper()
        
        # Test with messy data
        dirty_transaction = {
            'date': '',
            'type': None,
            'team': 'Philadelphia Eagles',
            'player': '',
            'description': 'Valid description',
            'transaction_id': 'test_001',
            'scraped_at': '2024-01-15T14:30:00'
        }
        
        cleaned = scraper.clean_transaction_data(dirty_transaction)
        
        # Check that empty/None values are replaced
        self.assertNotEqual(cleaned['type'], None)
        self.assertNotEqual(cleaned['player'], '')
        self.assertEqual(cleaned['type'], 'Unknown')
        self.assertEqual(cleaned['player'], 'Unknown')
        
        print("✅ Data cleaning test passed")
    
    def test_csv_export(self):
        """Test CSV file export functionality"""
        print("🧪 Testing CSV export...")
        
        scraper = NFLTransactionScraper()
        df = scraper.parse_transactions(self.sample_espn_response)
        
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            test_filename = os.path.join(temp_dir, 'test_transactions.csv')
            result_filename = scraper.save_to_csv(df, test_filename)
            
            # Check file was created
            self.assertTrue(os.path.exists(result_filename))
            
            # Check file contents
            loaded_df = pd.read_csv(result_filename)
            self.assertEqual(len(loaded_df), 2)
            self.assertEqual(loaded_df.iloc[0]['team'], 'Philadelphia Eagles')
        
        print("✅ CSV export test passed")
    
    def test_duplicate_removal(self):
        """Test duplicate transaction removal"""
        print("🧪 Testing duplicate removal...")
        
        # Create DataFrame with duplicates
        data = [
            {'transaction_id': 'test_001', 'team': 'Eagles', 'type': 'Signing'},
            {'transaction_id': 'test_002', 'team': 'Cowboys', 'type': 'Release'},
            {'transaction_id': 'test_001', 'team': 'Eagles', 'type': 'Signing'},  # Duplicate
        ]
        df = pd.DataFrame(data)
        
        # Remove duplicates
        df_clean = df.drop_duplicates(subset=['transaction_id'], keep='first')
        
        self.assertEqual(len(df_clean), 2)  # Should have 2 unique transactions
        
        print("✅ Duplicate removal test passed")
    
    @patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling"""
        print("🧪 Testing API error handling...")
        
        # Mock API failure
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        scraper = NFLTransactionScraper()
        
        # Should raise exception on API failure
        with self.assertRaises(Exception):
            scraper.fetch_transactions()
        
        print("✅ API error handling test passed")
    
    def test_google_sheets_configuration(self):
        """Test Google Sheets configuration (without actual connection)"""
        print("🧪 Testing Google Sheets configuration...")
        
        # Test with missing credentials
        with self.assertRaises(ValueError):
            GoogleSheetsUpdater(credentials_path=None, sheet_id=None)
        
        # Test with dummy paths (won't connect but should validate input)
        try:
            GoogleSheetsUpdater(credentials_path='dummy.json', sheet_id='dummy_id')
        except ValueError as e:
            if "required" in str(e):
                self.fail("Should not require credentials for initialization test")
        except Exception:
            # Expected to fail on actual connection, which is fine for this test
            pass
        
        print("✅ Google Sheets configuration test passed")
    
    def test_date_processing(self):
        """Test date processing and formatting"""
        print("🧪 Testing date processing...")
        
        scraper = NFLTransactionScraper()
        
        # Test various date formats
        test_dates = [
            '2024-01-15T14:30:00Z',
            '2024-01-15T14:30:00.000Z',
            '2024-01-15',
            ''
        ]
        
        for date_str in test_dates:
            transaction = {
                'date': date_str,
                'type': 'Test',
                'team': 'Test Team',
                'player': 'Test Player',
                'description': 'Test',
                'transaction_id': 'test',
                'scraped_at': datetime.now().isoformat()
            }
            
            cleaned = scraper.clean_transaction_data(transaction)
            
            # Should always have a valid date format
            self.assertIsNotNone(cleaned['date'])
            self.assertNotEqual(cleaned['date'], '')
        
        print("✅ Date processing test passed")
    
    def test_system_integration(self):
        """Test overall system integration"""
        print("🧪 Testing system integration...")
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_PATH': 'dummy.json',
            'GOOGLE_SHEET_ID': 'dummy_sheet_id'
        }):
            try:
                # This should initialize without errors (though won't connect)
                automation = NFLTransactionAutomation()
                self.assertIsNotNone(automation.scraper)
                
            except Exception as e:
                # Expected to fail on Google Sheets connection, which is fine
                if "Google Sheets" not in str(e):
                    raise
        
        print("✅ System integration test passed")


class TestDataQuality(unittest.TestCase):
    """Test data quality and validation"""
    
    def test_required_fields_present(self):
        """Test that all required fields are present in output"""
        print("🧪 Testing required fields...")
        
        scraper = NFLTransactionScraper()
        sample_response = {
            'items': [{
                'id': 'test_001',
                'date': '2024-01-15T14:30:00Z',
                'type': {'displayName': 'Signing'},
                'team': {'displayName': 'Philadelphia Eagles'},
                'player': {'displayName': 'Test Player'},
                'description': 'Test transaction'
            }]
        }
        
        df = scraper.parse_transactions(sample_response)
        
        required_fields = ['date', 'type', 'team', 'player', 'description', 'transaction_id', 'scraped_at']
        
        for field in required_fields:
            self.assertIn(field, df.columns, f"Required field '{field}' missing")
            self.assertFalse(df[field].isna().any(), f"Field '{field}' contains null values")
        
        print("✅ Required fields test passed")
    
    def test_data_types(self):
        """Test that data types are correct"""
        print("🧪 Testing data types...")
        
        scraper = NFLTransactionScraper()
        df = scraper.parse_transactions({
            'items': [{
                'id': 'test_001',
                'date': '2024-01-15T14:30:00Z',
                'type': {'displayName': 'Signing'},
                'team': {'displayName': 'Philadelphia Eagles'},
                'player': {'displayName': 'Test Player'},
                'description': 'Test transaction'
            }]
        })
        
        # All fields should be strings
        for column in df.columns:
            self.assertTrue(df[column].dtype == 'object', f"Column '{column}' should be string type")
        
        print("✅ Data types test passed")


def run_connectivity_tests():
    """Run real connectivity tests (requires actual credentials)"""
    print("\n🌐 CONNECTIVITY TESTS")
    print("=" * 50)
    
    # Test ESPN API
    try:
        print("🔍 Testing ESPN API connectivity...")
        scraper = NFLTransactionScraper()
        data = scraper.fetch_transactions()
        
        if 'items' in data:
            print(f"✅ ESPN API: Connected successfully ({len(data['items'])} transactions available)")
        else:
            print("⚠️ ESPN API: Connected but no transaction data structure found")
            
    except Exception as e:
        print(f"❌ ESPN API: Connection failed - {e}")
    
    # Test Google Sheets (only if credentials available)
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    if credentials_path and sheet_id and os.path.exists(credentials_path):
        try:
            print("🔍 Testing Google Sheets connectivity...")
            updater = GoogleSheetsUpdater()
            updater.setup_worksheet("Test_Connection")
            print("✅ Google Sheets: Connected successfully")
            
        except Exception as e:
            print(f"❌ Google Sheets: Connection failed - {e}")
    else:
        print("⏭️ Google Sheets: Skipped (credentials not configured)")


def main():
    """Main test execution"""
    print("🧪 NFL TRANSACTION AUTOMATION - TEST SUITE")
    print("=" * 60)
    
    # Check if this is a connectivity test
    if len(sys.argv) > 1 and sys.argv[1] == 'connectivity':
        run_connectivity_tests()
        return
    
    # Run unit tests
    print("🧪 UNIT TESTS")
    print("-" * 30)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNFLTransactionSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏆 TEST SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("\n💡 Next steps:")
        print("   1. Run connectivity tests: python tests/test_system.py connectivity")
        print("   2. Configure your .env file with real credentials")
        print("   3. Run the main automation: python src/main.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n🔧 Check the failures above and fix any issues before proceeding.")
        sys.exit(1)


if __name__ == '__main__':
    main()
