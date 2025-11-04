#!/bin/bash
# Setup script for Google Places MCP Server

echo "🚀 Setting up Google Places MCP Server..."
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment (optional but recommended)
echo ""
read -p "Create virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Setup environment file
echo ""
if [ ! -f .env ]; then
    echo "Setting up environment variables..."
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Google Maps API Key"
    echo "   Get your key from: https://console.cloud.google.com/google/maps-apis/"
else
    echo "✓ .env file already exists"
fi

# Test server
echo ""
echo "Testing server..."
python3 -m py_compile server.py
if [ $? -eq 0 ]; then
    echo "✓ Server code is valid"
else
    echo "✗ Server code has errors"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_MAPS_API_KEY"
echo "2. Ensure these APIs are enabled in Google Cloud Console:"
echo "   - Places API (New)"
echo "   - Routes API"
echo "   - Geocoding API"
echo "3. Add this server to your Claude Desktop config"
echo ""
echo "See README.md for detailed instructions."
