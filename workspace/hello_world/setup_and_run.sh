#!/bin/bash

# --- Configuration ---
PROJECT_DIR="$(dirname "$0")"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
APP_TARGET="app:app"
PORT=8000

set -e # Exit immediately if a command exits with a non-zero status.

echo "[SETUP] Navigating to project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

# --- 1. Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
    echo "[SETUP] Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "[SETUP] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# --- 2. Dependency Installation ---
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "[SETUP] Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "[ERROR] Requirements file not found at $REQUIREMENTS_FILE"
    exit 1
fi

# --- 3. Application Execution ---
echo "[RUN] Starting Uvicorn server for $APP_TARGET on port $PORT..."
echo "[INFO] Press Ctrl+C to stop the server."

# Use the python executable inside the venv to ensure correct pathing
# The --reload flag is useful for development, but for a final script, we might omit it.
# For this demonstration, we'll keep it simple and use the activated environment.
exec uvicorn $APP_TARGET --host 0.0.0.0 --port $PORT

# Deactivate is not strictly necessary here because 'exec' replaces the shell process,
# but for completeness if 'exec' were removed:
# deactivate
