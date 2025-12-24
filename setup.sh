#!/bin/bash
# Stock Advisor Pro - Setup and Run Script

echo "=========================================="
echo "Stock Advisor Pro - Setup"
echo "=========================================="

# Check Python version
echo "Checking Python installation..."
python3 --version || { echo "Python 3 not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or simply run: ./start.sh"
echo "=========================================="
