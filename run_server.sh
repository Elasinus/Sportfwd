#!/bin/bash

# Sportfwd Django App with WebSocket Support
# This script runs the Django app using Daphne ASGI server

echo "🚀 Starting Sportfwd Django App with WebSocket Support..."

# Set Django settings module
export DJANGO_SETTINGS_MODULE=sportfwd.settings

echo "✅ Virtual environment activated"

# Run Daphne ASGI server
echo "🌐 Starting Daphne ASGI server on http://127.0.0.1:8000"
echo "📡 WebSocket support enabled for real-time chat"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

daphne -b 0.0.0.0 -p 8000 sportfwd.asgi:application 
