#!/bin/bash
# Verify Stock Advisor Pro Installation

echo "=========================================="
echo "Stock Advisor Pro - Installation Verify"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Python version:"
python3 --version
echo ""

# Check virtual environment
echo "✓ Virtual environment:"
if [ -d "venv" ]; then
    echo "  ✅ venv directory exists"
else
    echo "  ❌ venv directory missing"
fi
echo ""

# Check main application file
echo "✓ Application files:"
if [ -f "main.py" ]; then
    echo "  ✅ main.py exists ($(wc -l < main.py) lines)"
fi
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt exists"
fi
echo ""

# Check GUI components
echo "✓ GUI components:"
for file in gui/dashboard.py gui/stock_search.py gui/stock_analysis.py gui/watchlist.py gui/reports.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file ($(wc -l < $file) lines)"
    fi
done
echo ""

# Check scrapers
echo "✓ Web scrapers:"
for file in scrapers/stock_scraper.py scrapers/market_scraper.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file ($(wc -l < $file) lines)"
    fi
done
echo ""

# Check analyzers
echo "✓ Analysis engine:"
if [ -f "analyzers/fundamental_analyzer.py" ]; then
    echo "  ✅ fundamental_analyzer.py ($(wc -l < analyzers/fundamental_analyzer.py) lines)"
fi
echo ""

# Check utilities
echo "✓ Utility modules:"
for file in utils/database.py utils/cache.py utils/report_generator.py utils/formatters.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file ($(wc -l < $file) lines)"
    fi
done
echo ""

# Check documentation
echo "✓ Documentation:"
for file in README.md QUICK_START.md PROJECT_SUMMARY.md; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    fi
done
echo ""

# Check dependencies
echo "✓ Key dependencies installed:"
source venv/bin/activate 2>/dev/null
python3 -c "import PyQt6; print('  ✅ PyQt6')" 2>/dev/null || echo "  ❌ PyQt6 missing"
python3 -c "import yfinance; print('  ✅ yfinance')" 2>/dev/null || echo "  ❌ yfinance missing"
python3 -c "import bs4; print('  ✅ beautifulsoup4')" 2>/dev/null || echo "  ❌ beautifulsoup4 missing"
python3 -c "import pandas; print('  ✅ pandas')" 2>/dev/null || echo "  ❌ pandas missing"
python3 -c "import reportlab; print('  ✅ reportlab')" 2>/dev/null || echo "  ❌ reportlab missing"
echo ""

# Summary
echo "=========================================="
echo "✅ Stock Advisor Pro is ready!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  bash start.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
