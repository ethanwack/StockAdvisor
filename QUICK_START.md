# Stock Advisor Pro - Quick Start Guide

## ⚡ 30-Second Setup

```bash
# 1. Navigate to StockAdvisor
cd /Users/ethan/StockAdvisor

# 2. Run setup (one-time)
bash setup.sh

# 3. Start the app
bash start.sh
```

That's it! The GUI will open.

## 🎯 First Time Using the App

### 1. Dashboard Tab (Home)
- You'll see major market indices
- Your watchlist summary
- Recent analyses
- Click **🔄 Refresh** to update data

### 2. Stock Search Tab
- Type a stock symbol (e.g., AAPL, MSFT, GOOGL)
- Or search by company name
- See quick metrics: P/E, dividend yield, market cap
- Double-click any stock to analyze

### 3. Analysis Tab
- Enter a stock symbol: **AAPL**
- Click **🔍 Analyze**
- Get a Quality Score (0-100)
- See investment thesis
- View analyst ratings

### 4. Watchlist Tab
- Add stocks you're interested in
- Add target prices
- Write personal notes
- Track over time

### 5. Reports Tab
- Generate professional reports
- Export as PDF, HTML, or Excel
- Share or save for records

## 📊 Understanding Quality Scores

```
80-100: Excellent  ⭐⭐⭐⭐⭐ (Strong Buy)
60-79:  Good       ⭐⭐⭐⭐   (Buy)
40-59:  Fair       ⭐⭐⭐     (Hold)
0-39:   Poor       ⭐⭐      (Sell/Avoid)
```

Score is based on:
- **P/E Ratio** - Valuation
- **Profit Margins** - Profitability  
- **Debt Ratio** - Financial Health
- **Growth Rate** - Expansion
- **Dividend Yield** - Income

## 🔧 Example Workflow

1. **Search for tech stocks**
   - Go to Stock Search tab
   - Filter by P/E < 30, Dividend > 0
   - See results

2. **Analyze top results**
   - Click on a stock
   - View detailed metrics
   - Read investment thesis
   - Check if analyst ratings agree

3. **Save to Watchlist**
   - Watchlist tab → Add stock
   - Set target price ($150)
   - Add notes ("Strong fundamentals")

4. **Generate Report**
   - Reports tab
   - Select stock from dropdown
   - Generate PDF
   - Share or keep for records

## 💡 Pro Tips

1. **Cache**: First lookup takes ~2 seconds, subsequent lookups are instant
2. **Refresh**: Click refresh to get latest data (clears 4-hour cache)
3. **Notes**: Use watchlist notes to track why you're interested in a stock
4. **Reports**: Generate reports before major investment decisions
5. **Watchlist**: Start with 5-10 stocks to track closely

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| Slow first load | First lookup scrapes data; cached after |
| No analyst ratings | Some stocks may not have available ratings |
| GUI won't open | Try: `export QT_QPA_PLATFORM_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.x/site-packages/PyQt6/Qt6/plugins` |

## 📚 What Gets Stored Locally

- ✅ `stock_advisor.db` - Your watchlist and notes (encrypted)
- ✅ `.cache/` - Scraped data (auto-clears after 4 hours)
- ✅ `reports/` - Generated PDF/HTML reports

**Nothing is sent anywhere** - All data stays on your computer!

## 🚀 Next Steps

1. ✅ Run the app: `bash start.sh`
2. ✅ Search for a stock: AAPL, MSFT, or TSLA
3. ✅ Analyze it
4. ✅ Add to watchlist
5. ✅ Generate a report

---

**Questions?** Check README.md for detailed documentation.

**Ready?** → `bash start.sh` 🎯

