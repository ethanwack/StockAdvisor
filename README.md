# Stock Advisor Pro - Python GUI Application

A professional stock research and analysis tool inspired by Motley Fool, featuring web scraping capabilities and fundamental analysis.

## Features

✨ **Core Capabilities:**
- 📊 **Dashboard** - Market overview with indices and watchlist summary
- 🔍 **Stock Search** - Find and filter stocks by valuation metrics
- 📈 **Deep Analysis** - Fundamental analysis with quality scoring
- 💬 **ChatBot** - AI-powered investment advisor and stock recommendation engine
- ⭐ **Watchlist** - Track favorite stocks with notes and targets
- 📄 **Reports** - Generate PDF/HTML analysis reports

✅ **Analysis Features:**
- Fundamental metrics (P/E, P/B, debt ratios, margins)
- Quality scoring system (0-100)
- Investment thesis generation
- Financial data scraping from multiple sources
- Analyst ratings aggregation
- News and sentiment tracking
- Historical price analysis

🤖 **ChatBot Features:**
- Stock recommendations and analysis
- Buy/sell signal strategies
- Shorting guidance and risk warnings
- Portfolio management advice
- Market analysis and trends
- Risk management techniques
- Works in rule-based mode or with OpenAI API for enhanced responses

## Project Structure

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
├── analyzers/             # Financial analysis modules
│   └── fundamental_analyzer.py  # Fundamental analysis engine
├── services/              # Service modules
│   ├── portfolio_service.py
│   ├── recommendation_service.py
│   ├── stock_service.py
│   └── chatbot_service.py # ChatBot AI engine (NEW!)
└── utils/                 # Utility modules
    ├── database.py        # SQLite database management
    ├── cache.py           # Data caching
    ├── report_generator.py # PDF/HTML/Excel reports
    └── formatters.py      # Number/currency formatting
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone or download the project:**
```bash
cd StockAdvisor
```

2. **Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

The GUI will launch with a professional dark theme and tabbed interface.

## Usage Guide

### Dashboard Tab
- View S&P 500, NASDAQ, Dow Jones indices
- See watchlist summary
- Monitor recent analyses
- **Refresh Button:** Updates all market data

### Stock Search Tab
- Search by symbol or company name
- Filter by P/E ratio, dividend yield
- View comparison metrics
- Double-click to view detailed analysis

### Analysis Tab
- Enter stock symbol
- View comprehensive financial metrics
- Get quality score (0-100)
- Read AI-generated investment thesis
- See analyst ratings

### Watchlist Tab
- Add stocks to track
- Set target prices
- Add personal research notes
- Track quality scores over time
- Double-click to view analysis

### Reports Tab
- Generate professional reports
- Export as PDF, HTML, or Excel
- Include financial summary and investment thesis
- Save for sharing or archival

## Analysis Scoring System

**Quality Score (0-100):**
- **80-100:** Excellent - Strong buy signal
- **60-79:** Good - Favorable fundamentals
- **40-59:** Fair - Mixed signals
- **0-39:** Poor - Weak fundamentals

**Components:**
- 25% Valuation (P/E, P/B ratios)
- 25% Profitability (margins, ROE)
- 20% Growth metrics
- 20% Financial Health (debt, equity)
- 10% Dividend yield

## Data Sources

The application scrapes and aggregates data from:
- **Yahoo Finance** - Real-time quotes, financials, news
- **SEC Filings** - 10-K, 10-Q documents (via parsing)
- **MarketWatch** - Analyst ratings and estimates
- **Multiple sources** - Historical data, sector performance

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

### GUI not rendering
- On macOS: May need `export QT_QPA_PLATFORM_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.x/site-packages/PyQt6/Qt6/plugins`

## Performance Tips

1. **Cache clearing:** Older cached data is auto-deleted
2. **Large watchlists:** Keep under 50 stocks for best performance
3. **Network:** First-time data fetch takes longer; subsequent calls use cache
4. **Reports:** PDF generation takes a few seconds; normal

## Future Enhancements

- [ ] Portfolio tracking with cost basis
- [ ] Screener with advanced filters
- [ ] Real-time price alerts
- [ ] Historical analysis charts
- [ ] Machine learning predictions
- [ ] Email report delivery
- [ ] Mobile companion app

## Requirements

See `requirements.txt` for full list:
- PyQt6 - GUI framework
- yfinance - Stock data
- beautifulsoup4 - Web scraping
- pandas/numpy - Data analysis
- reportlab - PDF generation
- matplotlib/seaborn - Charts

## License

Personal use - Modify as needed for your research

## Contributing

This is a personal research tool. Feel free to extend and customize!

## Support

For issues:
1. Check troubleshooting section
2. Review logs in application directory
3. Check data source availability

---

**Happy researching!** 🎯📈

Stock Advisor Pro v1.0 - Built for thoughtful investors
