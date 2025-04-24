#!/bin/bash

# Exit on error
set -e

# Make sure we're in the project root
cd "$(dirname "$0")"

# Start the backend WebSocket server in the background
echo "Starting Python WebSocket server..."
PYTHONPATH=$(pwd) python3 -m server.server &

# Save the backend's PID so we can kill it later
BACKEND_PID=$!

# Start the HTTP server for the frontend
echo "Starting HTTP server for the frontend (http://localhost:8080)..."
cd web
python3 -m http.server 8080

# When HTTP server exits, stop the backend
echo "Shutting down backend server..."
kill $BACKEND_PID
