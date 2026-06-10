#!/usr/bin/env bash
# AIM Installer for macOS and Linux
# Usage: curl -fsSL https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.sh | bash

set -e

echo "=== AIM (AI Memory/Mind) Installer for macOS/Linux ==="

# 1. Detect Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "[-] Error: Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/ or your system package manager."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &>/dev/null; then
    PYTHON_CMD="python"
fi

echo "[+] Found Python: $($PYTHON_CMD --version)"

# 2. Detect / Install pip
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo "[*] pip not found. Attempting to bootstrap pip..."
    $PYTHON_CMD -m ensurepip --default-pip || {
        echo "[-] Error: Failed to bootstrap pip automatically."
        echo "Please install pip manually and re-run this script."
        exit 1
    }
fi

# 3. Install AIM via pip from the Git repository
REPO_URL="git+https://github.com/phuonghx/aim-cli.git"

echo "[*] Installing AIM CLI from: $REPO_URL ..."
$PYTHON_CMD -m pip install --upgrade "$REPO_URL"

echo ""
echo "========================================="
echo "   [+] AIM installed successfully!       "
echo "========================================="
echo "You can now run 'aim' command directly from your terminal."
echo "Run 'aim init' in your project directory to get started."
echo "========================================="
