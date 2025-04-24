#!/bin/bash

# Exit on error
set -e

# Make sure we're in the project root
cd "$(dirname "$0")"

# Start the backend WebSocket server in the background
echo "Starting Python WebSocket server..."
PYTHONPATH=$(pwd) python3 -m server.server