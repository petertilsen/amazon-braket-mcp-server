#!/bin/sh
# Simple health check for the MCP server
# This script checks if the server is responding to HTTP requests

set -e

HOST="localhost"
PORT="8080"
ENDPOINT="/health"

curl -f "http://${HOST}:${PORT}${ENDPOINT}" || exit 1
