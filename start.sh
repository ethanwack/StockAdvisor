#!/bin/bash
# Stock Advisor Pro - Run Script

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
    source venv/bin/activate
}

# Run application
echo "Starting Stock Advisor Pro..."
python main.py
