#!/bin/bash
# Quick Start Script for Russian Roulette Multiplayer Game
# This script activates the virtual environment and starts the server

set -e

echo "🎯 Russian Roulette - Quick Start"
echo "================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the russian-roulette directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python setup.py"
    exit 1
fi

# Activate virtual environment and start server
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Starting server..."
echo ""

python run.py
