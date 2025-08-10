#!/bin/bash
# RouteForce Filesystem MCP Server Launcher
# Usage: ./start-filesystem-server.sh [path1] [path2] [...]

cd "$(dirname "$0")"

# Build if needed
if [ ! -d "build" ] || [ "src/filesystem.ts" -nt "build/filesystem.js" ]; then
    echo "Building MCP filesystem server..."
    npm run build
fi

# Default paths if none provided
if [ $# -eq 0 ]; then
    echo "Starting RouteForce Filesystem MCP Server with default paths..."
    echo "Allowed paths:"
    echo "  - $(pwd)/.."
    echo "  - $(pwd)/../app"
    echo "  - $(pwd)/../frontend"
    echo ""
    node build/filesystem.js "$(pwd)/.." "$(pwd)/../app" "$(pwd)/../frontend"
else
    echo "Starting RouteForce Filesystem MCP Server with custom paths..."
    echo "Allowed paths:"
    for path in "$@"; do
        echo "  - $path"
    done
    echo ""
    node build/filesystem.js "$@"
fi
