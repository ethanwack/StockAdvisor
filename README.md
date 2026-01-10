# 📊 Stock Advisor Pro - Professional Stock Research Tool

A stock research and analysis platform inspired by Motley Fool. Analyze stocks, get quality scores, build watchlists, and make better investment decisions.

**Works on:** Mac, Windows, Linux  
**No coding experience needed** ✅  
**Free & open-source**  

---

## ⚡ QUICK INSTALL (Copy & Paste)

```bash
git clone https://github.com/ethanwack/StockAdvisor.git
cd StockAdvisor
python3 main.py
```

**That's it!** ☝️ Run those 3 commands in your terminal/command prompt. The app opens automatically.

---

## 📖 CHOOSE YOUR PATH

| **You are...** | **Do this** |
|---|---|
| **Never used a terminal before** | 👉 [START HERE: Beginner Guide](./GETTING_STARTED.md) (has screenshots) |
| **Know how to use terminal** | ☝️ Copy the 3 commands above & run them |
| **Developer/Advanced** | See "For Developers" section below |

---

## 🚀 Getting Started (5-10 Minutes)

### ⚠️ NEW TO COMPUTERS/TERMINALS? 
**→ [READ THIS FIRST: Complete Beginner Guide](./GETTING_STARTED.md)**

This guide has screenshots and walks you through:
- ✅ How to download the code (3 methods explained with pictures)
- ✅ How to install Python (step-by-step for Mac/Windows/Linux)
- ✅ How to run the program (exact steps, no guessing)
- ✅ What to do if something goes wrong (troubleshooting)

**Seriously - if you've never used a terminal, start there!**

---

### I Already Know What I'm Doing (Quick Start)

#### Method 1: Using the Menu Script (Easiest)
```bash
git clone https://github.com/ethanwack/StockAdvisor.git
cd StockAdvisor
./run-app.sh
```
Then select what you want to run from the menu.

#### Method 2: Run Desktop App Directly
```bash
cd StockAdvisor
python3 main.py
```

#### Method 3: Run Everything (3 separate terminals)
```bash
# Terminal 1 - Desktop App
python3 main.py

# Terminal 2 - Mobile App
cd mobile && npm start

# Terminal 3 - Web App
cd frontend && npm start
```

---

## ⚙️ What You Need to Install This

**Before you start, you'll need to install 2 things:**

### 1. Python 3.8 or newer
**What is Python?** It's the programming language this app is written in.

- **Mac:** Already has Python! Just open Terminal and type: `python3 --version`
- **Windows:** Download from [python.org](https://www.python.org/downloads) (choose the latest version)
- **Linux:** Install with: `sudo apt install python3 python3-pip`

### 2. Git (Optional, but recommended)
**What is Git?** It's used to download the code from GitHub.

- **Mac:** Already installed! Open Terminal to verify: `git --version`
- **Windows:** Download from [git-scm.com](https://git-scm.com/download/win)
- **Linux:** Install with: `sudo apt install git`

**Don't have Git?** No problem - you can download the code as a ZIP file instead. See the beginner guide.

---

## 📚 What This App Does

✨ **Core Features:**
- 📊 **Dashboard** - See market overview and your watchlist at a glance
- 🔍 **Stock Search** - Find stocks and filter by quality metrics
- 📈 **Analysis** - Get detailed financial breakdown with a 0-100 quality score
- 💬 **AI ChatBot** - Ask investment questions and get AI-powered answers
- ⭐ **Watchlist** - Track stocks you're interested in with notes
- 📄 **Reports** - Export analysis as PDF, HTML, or Excel files

✅ **Analysis Metrics Included:**
- Company valuation (P/E ratio, Price-to-Book)
- Profitability (profit margins, ROE)
- Growth rates (revenue, earnings)
- Financial health (debt levels, equity)
- Dividend yields
- Quality score (AI-generated)
- Investment thesis (AI-written)

🤖 **ChatBot can help with:**
- "Is this stock a good buy?"
- "What's a good entry price?"
- "How much risk does this have?"
- "Should I sell this position?"
- General investment questions

---

```
StockAdvisor/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── gui/                    # PySide6 GUI components
│   ├── dashboard.py       # Dashboard tab (with fallback data)
│   ├── stock_search.py    # Stock search tab
│   ├── stock_analysis.py  # Analysis tab
│   ├── chatbot.py         # ChatBot tab (NEW!)
│   ├── watchlist.py       # Watchlist tab
│   └── reports.py         # Reports tab
├── scrapers/              # Web scraping modules
│   ├── stock_scraper.py   # Stock data scraper (Yahoo Finance)
│   └── market_scraper.py  # Market indices scraper
---

## 🖥️ How to Download the Code

**Choose ONE method below:**

### Method A: Using Git (Recommended if you have it)
Open Terminal/Command Prompt and type:
```bash
git clone https://github.com/ethanwack/StockAdvisor.git
cd StockAdvisor
```

### Method B: Using GitHub Desktop (Easiest GUI method)
1. Go to [github.com/ethanwack/StockAdvisor](https://github.com/ethanwack/StockAdvisor)
2. Click the green **"Code"** button
3. Click **"Open with GitHub Desktop"**
4. Choose where to save it
5. Done! You now have the code

### Method C: Download as ZIP file (No tools needed)
1. Go to [github.com/ethanwack/StockAdvisor](https://github.com/ethanwack/StockAdvisor)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the file by double-clicking it
5. Rename the folder to "StockAdvisor" (optional, but cleaner)

---

## 🚀 How to Run It

Once you have the code downloaded:

### Step 1: Open Terminal/Command Prompt
- **Mac:** Applications → Utilities → Terminal
- **Windows:** Search for "Command Prompt" or "PowerShell"
- **Linux:** Open your terminal app

### Step 2: Go to the Project Folder
```bash
cd StockAdvisor
```
(Replace "StockAdvisor" with wherever you saved it)

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```
This downloads and installs all the code this app needs to run.
**This takes a few minutes - that's normal!**

### Step 4: Run the App
```bash
python3 main.py
```

**🎉 The app should open! A window will appear with the stock research interface.**

---

## ❓ Getting Help

**Something didn't work?**
- Check the [GETTING_STARTED.md](./GETTING_STARTED.md) guide (has screenshots!)
- Look at the Troubleshooting section below
- Check that you installed Python correctly

**Have a question?**
- See the Usage Guide section below
- Try hovering over buttons in the app (many have help tooltips)

---

## 📖 How to Use the App

### Dashboard Tab
**What you'll see:** Market overview with major indices and your watchlist

- **Indices Display:** Shows S&P 500, NASDAQ, Dow Jones performance
- **Watchlist Summary:** Quick glance at your tracked stocks
- **Refresh Button:** Manually update all data

### Stock Search Tab
**What you'll do:** Find stocks to analyze

1. Type a stock symbol (e.g., "AAPL" for Apple) or company name
2. Press Enter or click Search
3. See results with key metrics (P/E ratio, dividend yield, etc.)
4. Double-click any result to see detailed analysis

### Analysis Tab
**What you'll see:** Deep dive into a stock's financials

1. Enter a stock symbol
2. The app shows:
   - All key financial metrics
   - **Quality Score (0-100):** How good an investment this is
   - **Investment Thesis:** AI-generated explanation of why this stock scores that way
   - Analyst ratings

**Quality Score Explained:**
- **80-100:** Excellent investment - strong buy signal
- **60-79:** Good fundamentals - consider buying
- **40-59:** Mixed signals - do more research
- **0-39:** Weak fundamentals - risky investment

### Watchlist Tab
**What you'll do:** Track stocks you're interested in

1. Add stocks you want to monitor
2. Set target prices (what you'd pay)
3. Add personal research notes
4. See quality scores update over time
5. Double-click any stock to see full analysis

### Reports Tab
**What you'll do:** Export your analysis

1. Generate professional reports
2. Export as PDF (best for printing/sharing) or Excel (best for data)
3. Reports include all analysis and metrics
4. Perfect for keeping records or sharing with advisors

---

## ⚠️ Troubleshooting

### Problem: "Python not found" or "command not recognized"
**Solution:**
- Make sure Python is installed (see Requirements section)
- On Mac, try `python3` instead of `python`
- Restart your terminal after installing Python

### Problem: "pip: command not found"
**Solution:**
- On Mac: Try `pip3` instead of `pip`
- On Windows: May need to reinstall Python and check "Add Python to PATH"

### Problem: "No module named 'PyQt6'"
**Solution:**
```bash
pip install PyQt6
```

### Problem: Network errors when trying to analyze stocks
**Solution:**
- Check your internet connection
- Yahoo Finance (the data source) might be temporarily down
- Try again in a few minutes
- Cached data will still work for recently analyzed stocks

### Problem: Database is locked
**Solution:**
```bash
rm stock_advisor.db
```
Then restart the app. It will create a fresh database.

### Problem: The app looks blurry or fonts are too small
**Solution:**
- This is normal on high-resolution displays
- Most features still work fine
- You can adjust your display scale in your OS settings

---

## 🔧 For Developers (Technical Details)

### Project Structure
```
StockAdvisor/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── gui/                    # User interface
│   ├── dashboard.py       # Main dashboard screen
│   ├── stock_search.py    # Search functionality
│   ├── stock_analysis.py  # Detailed analysis
│   ├── chatbot.py         # AI assistant
│   ├── watchlist.py       # Watchlist management
│   └── reports.py         # Report generation
├── scrapers/              # Data collection
│   ├── stock_scraper.py   # Fetches stock data
│   └── market_scraper.py  # Gets market indices
├── analyzers/             # Analysis engines
│   └── fundamental_analyzer.py
├── services/              # Business logic
│   ├── portfolio_service.py
│   ├── recommendation_service.py
│   ├── stock_service.py
│   └── chatbot_service.py
└── utils/                 # Helper functions
    ├── database.py        # SQLite database
    ├── cache.py           # Data caching
    ├── report_generator.py
    └── formatters.py
```

### Data Storage
- **Database:** SQLite file (`stock_advisor.db`) - stores watchlists, analysis, history
- **Cache:** `.cache/` folder - stores downloaded data for 4 hours
- **Auto-created:** Both are created automatically on first run

### Caching System
- Downloaded data is cached for 4 hours
- Reduces API calls and makes the app faster
- Old cache is automatically cleaned up
- You can clear cache manually by deleting `.cache/` folder

---

## 📊 Analysis Scoring System

The app gives each stock a **Quality Score from 0-100** based on:

- **Valuation (25%):** P/E ratio, Price-to-Book ratio
- **Profitability (25%):** Profit margins, Return on Equity
- **Growth (20%):** Revenue and earnings growth rates
- **Financial Health (20%):** Debt levels, equity ratio
- **Income (10%):** Dividend yield

**Example:** Apple might get 85 (excellent), a risky startup might get 35 (poor)

---

## 🌐 Data Sources

The app gets information from:
- **Yahoo Finance:** Real-time prices, company financials, news
- **SEC Filings:** Official company reports
- **MarketWatch:** Analyst ratings and estimates
- Multiple sources for accuracy and validation

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quit application |
| `Ctrl+R` | Refresh current tab |
| `Ctrl+S` | Save/Export report |
| `Enter` | Search/Analyze (in input fields) |

## Database

The application uses SQLite to store:
- Watchlist stocks and notes
- Analysis history and scores
- Price history data
- Generated reports

Database file: `stock_advisor.db` (auto-created)

## Caching

Scraped data is cached for 4 hours to reduce API calls:
- Cache directory: `.cache/`
- Automatically managed
- TTL configurable in `cache.py`

## Configuration

Edit `main.py` to customize:
- Default window size
- Theme colors
- Cache TTL
- Database location

## Troubleshooting

### ImportError: No module named 'PyQt6'
```bash
pip install PyQt6
```

### Network errors when scraping
- Check internet connection
- Some data sources may have rate limiting
- Cache will provide previous data

### Database locked error
- Close other instances of the app
- Delete `stock_advisor.db` and restart (will recreate)

### Problem: The app looks blurry or fonts are too small
**Solution:**
- This is normal on high-resolution displays
- Most features still work fine
- You can adjust your display scale in your OS settings

---

## 💡 Tips for Best Results

1. **Fresh Data:** Click the refresh button to get latest prices
2. **Watchlist Size:** Keep under 50 stocks for faster performance
3. **First Load:** First time analyzing a stock takes longer (data download)
4. **Exports:** PDF reports take a few seconds to generate - that's normal
5. **Accuracy:** This tool is for research - always do your own due diligence!

---

## 📦 Technical Dependencies

The app uses these Python libraries (auto-installed):
- **PyQt6** - Creates the user interface
- **yfinance** - Downloads stock data from Yahoo Finance
- **beautifulsoup4** - Reads web pages for financial data
- **pandas/numpy** - Analyzes financial data
- **reportlab** - Generates PDF reports

See `requirements.txt` for full list.

---

## ❓ FAQ

**Q: Is this free?**
A: Yes! It's open-source and completely free.

**Q: Can I modify this for my own use?**
A: Absolutely! It's yours to customize.

**Q: Does this make trades automatically?**
A: No. It only analyzes stocks and gives recommendations.

**Q: Can I use real-time data?**
A: Yes, but it's limited by the free data sources (Yahoo Finance, etc.)

**Q: What if I don't understand a metric?**
A: Hover over button/fields in the app - many have help tooltips!

**Q: Can I run this on a server?**
A: The GUI version needs a display, but the backend can be adapted for server use.

---

## 🎉 You're All Set!

1. ✅ Installed Python
2. ✅ Downloaded the code
3. ✅ Installed dependencies with `pip install -r requirements.txt`
4. ✅ Ran with `python3 main.py`
5. ✅ Ready to analyze stocks!

**Questions?** Check the [GETTING_STARTED.md](./GETTING_STARTED.md) guide or review the troubleshooting section above.

---

**Happy researching!** 🎯📈  
**Stock Advisor Pro** - Made for thoughtful investors
