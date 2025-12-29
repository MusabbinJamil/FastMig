#!/bin/bash

set -e  # Exit on error

echo "========================================"
echo "FastMig Frontend Starter"
echo "========================================"
echo ""

# Use native Flutter (not Windows)
export PATH="$HOME/flutter/bin:$PATH"

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/flutter-frontend-app"
echo "[DEBUG] Working in: $(pwd)"

echo "[DEBUG] Flutter: $(which flutter)"
echo "[DEBUG] Version: $(flutter --version | head -1)"

echo "[DEBUG] Enabling web support..."
flutter config --enable-web 2>/dev/null || true

echo ""
echo "Starting Flutter Web Server..."
echo "Open http://localhost:8080 in your browser"
echo ""

flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0

echo ""
echo "App stopped"
