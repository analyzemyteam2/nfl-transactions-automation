# NFL Transaction Automation - Complete Setup Guide
## 🚀 Get Your Automated Pipeline Running in 30 Minutes

This guide walks you through setting up the complete NFL transaction automation pipeline from ESPN API → Google Sheets → Airtable.

---

## 📋 **OVERVIEW**
ESPN API → GitHub Actions → Google Sheets → Zapier → Airtable
↓           ↓              ↓           ↓        ↓
Daily Data → Automation → Structured → Sync → Final DB

## 🛠️ **STEP 1: Google Cloud Setup (10 minutes)**

### **Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project"
3. Name: `nfl-transactions-automation`
4. Click "Create"

### **Enable Google Sheets API**
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click "Enable"

### **Create Service Account**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: `nfl-transaction-bot`
4. Role: `Editor`
5. Click "Create"

### **Download Credentials**
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON"
5. Download the file (save as `google_credentials.json`)

## 📊 **STEP 2: Google Sheets Setup (5 minutes)**

### **Create Your Spreadsheet**
1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet
3. Name it: `NFL Transactions Database`
4. Copy the Sheet ID from URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`

### **Share with Service Account**
1. Click "Share" in your Google Sheet
2. Add the service account email (from your credentials JSON file)
3. Give "Editor" permissions
4. Click "Send"

## 🔐 **STEP 3: GitHub Secrets Configuration (5 minutes)**

In your GitHub repository, go to "Settings" → "Secrets and variables" → "Actions"

### **Add these Repository Secrets:**

#### **GOOGLE_CREDENTIALS_BASE64**
```bash
# On your computer, convert the credentials file to base64:
# Mac/Linux:
base64 -i google_credentials.json

# Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("google_credentials.json"))
Copy the output and add as secret GOOGLE_CREDENTIALS_BASE64
GOOGLE_SHEET_ID
# From your Google Sheets URL
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
                                    ^^^^^^^^^^^^^^^^^^^^
                                    This is your SHEET_ID
SLACK_WEBHOOK_URL (Optional)
If you want Slack notifications:

Create Slack webhook in your workspace
Add the webhook URL as this secret

🧪 STEP 4: Test Your Setup (5 minutes)
Manual Test Run

Go to "Actions" tab in your GitHub repository
Click "Daily NFL Transaction Scraper"
Click "Run workflow"
Check "Run in test mode"
Click "Run workflow"

Check Results

✅ Workflow should complete successfully
✅ Check your Google Sheet for test data
✅ Review logs in the Actions tab

🔄 STEP 5: Zapier Integration (5 minutes)
Connect Google Sheets to Zapier

Go to Zapier
Create new Zap
Trigger: "Google Sheets" → "New Spreadsheet Row"
Connect your Google account
Select your NFL Transactions spreadsheet
Select "NFL_Transactions" worksheet

Connect Zapier to Airtable

Action: "Airtable" → "Create Record"
Connect your Airtable account
Select your base and table
Map fields:

Date → Date field
Type → Transaction Type
Team → Team field
Player → Player field
Description → Notes field



Test and Activate

Test the Zap with sample data
Turn on the Zap
Set to run every 15 minutes


📅 DAILY AUTOMATION SCHEDULE
TimeActionDescription9:00 AM ESTGitHub Actions TriggersDaily workflow starts9:01 AM ESTESPN API ScrapingFetch new transactions9:02 AM ESTGoogle Sheets UpdateAdd new data, filter duplicates9:05 AM ESTZapier SyncEvery 15 minutes to Airtable9:20 AM ESTFinal Data AvailableComplete in all systems
🔧 TROUBLESHOOTING
Common Issues & Solutions
GitHub Actions Failing
❌ Error: Google Sheets authentication failed
✅ Solution: Check GOOGLE_CREDENTIALS_BASE64 secret is correct
❌ Error: Sheet not found
✅ Solution: Verify GOOGLE_SHEET_ID and service account permissions
No Data in Google Sheets
❌ Issue: Workflow runs but no data appears
✅ Check: ESPN API might have no transactions for that day
✅ Check: Look at workflow logs for error messages
Zapier Not Syncing
❌ Issue: Google Sheets updates but Airtable doesn't
✅ Check: Zapier is turned on and field mappings are correct
✅ Check: Airtable permissions and base configuration
Manual Commands
Test Connectivity
Go to Actions → Daily NFL Transaction Scraper → Run workflow → Check "test mode"
Process Specific Date
Run workflow manually and enter date in YYYY-MM-DD format
Historical Backfill
yaml# Edit workflow file temporarily to add:
python src/main.py backfill 2024-01-01 2024-01-31
📊 DATA STRUCTURE
Google Sheets Columns
ColumnDescriptionExampleDateTransaction date2024-01-15TypeTransaction typeSigning, Trade, ReleaseTeamNFL team namePhiladelphia EaglesPlayerPlayer nameJalen HurtsDescriptionFull details"Signed to reserve/future contract"Transaction IDUnique identifierESPN_12345Scraped AtWhen collected2024-01-15T14:30:00
Airtable Fields (Recommended)

Date (Date field)
Transaction Type (Single select: Signing, Trade, Release, Waiver, IR)
Team (Single select with all 32 NFL teams)
Player (Single line text)
Position (Single select with positions)
Notes (Long text for description)
Source (Single line text: "ESPN API")
Imported At (Date field)

🎯 CUSTOMIZATION OPTIONS
Change Schedule
Edit .github/workflows/daily_nfl_scraper.yml:
yamlschedule:
  - cron: '0 16 * * *'  # 4 PM UTC = 11 AM EST
Filter Transaction Types
Edit src/transaction_scraper.py to filter specific types:
python# Only get signings and trades
allowed_types = ['Signing', 'Trade']
df = df[df['type'].isin(allowed_types)]
Add More Data Sources
Extend transaction_scraper.py to include additional APIs or websites.
💡 OPTIMIZATION TIPS
Performance

✅ System processes ~100-200 transactions per day efficiently
✅ GitHub Actions free tier provides 2,000 minutes/month (plenty)
✅ Google Sheets API has generous free limits

Reliability

✅ Automatic retry logic for API failures
✅ CSV backup of all data
✅ Duplicate prevention
✅ Error notifications

Monitoring

✅ Check GitHub Actions tab for daily run status
✅ Review Google Sheets metadata tab for last update time
✅ Monitor Zapier dashboard for sync status


🏆 CONGRATULATIONS!
Your NFL transaction automation is now running! The system will:
✅ Automatically scrape NFL transactions every day at 9 AM EST
✅ Update Google Sheets with clean, structured data
✅ Sync to Airtable via Zapier every 15 minutes
✅ Handle errors gracefully with retries and notifications
✅ Prevent duplicates and maintain data integrity
You'll never need to manually track NFL transactions again! 🏈⚡
📞 SUPPORT

Issues: Create GitHub issue in this repository
Questions: Check troubleshooting section above
Enhancements: Submit feature requests via GitHub issues


Happy automating! 🚀📊🏈

**Commit Message:**
Add comprehensive setup guide for Google Sheets, GitHub Actions, and Zapier integration

**Brief Extended Description:**
This complete setup guide provides step-by-step instructions for configuring the entire NFL transaction automation pipeline. It covers:
- Google Cloud and Sheets API setup with service accounts
- GitHub repository secrets configuration
- Testing procedures to verify everything works
- Zapier integration for Google Sheets → Airtable sync
- Troubleshooting common issues
- Data structure documentation
- Customization options and optimization tips

This guide ensures anyone can set up the complete automation system from scratch, even without technical expertise. It's the missing piece that makes the repository truly plug-and-play.

---

**Ready to add this file? Tell me when you've added it and I'll give you the next step!** 🚀
