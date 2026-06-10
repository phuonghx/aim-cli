# AIM Installer for Windows PowerShell
# Usage: iwr -useb https://raw.githubusercontent.com/phuonghx/aim-cli/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "=== AIM (AI Memory/Mind) Installer for Windows ===" -ForegroundColor Cyan

# 1. Detect Python. On Windows, prefer "python" / "py -3" - "python3" is
# usually the Microsoft Store alias stub that opens the Store instead.
$pythonCmd = $null
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Error "[-] Error: Python is required but not found in your PATH."
    Write-Host "Please install Python from https://www.python.org/ and check 'Add Python to PATH'." -ForegroundColor Yellow
    exit 1
}

$pyVersion = & $pythonCmd --version
Write-Host "[+] Found Python: $pyVersion" -ForegroundColor Green

# 2. Detect / Install pip
$hasPip = & $pythonCmd -m pip --version 2>$null
if (-not $hasPip) {
    Write-Host "[*] pip not found. Attempting to bootstrap pip..." -ForegroundColor Yellow
    try {
        & $pythonCmd -m ensurepip --default-pip
    } catch {
        Write-Error "[-] Error: Failed to bootstrap pip automatically. Please install pip manually."
        exit 1
    }
}

# 3. Install AIM via pip from the Git repository
$repoUrl = "git+https://github.com/phuonghx/aim-cli.git"

Write-Host "[*] Installing AIM CLI from: $repoUrl ..." -ForegroundColor Yellow
& $pythonCmd -m pip install --upgrade $repoUrl

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "   [+] AIM installed successfully!       " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "You can now run 'aim' command directly from your terminal."
Write-Host "Run 'aim init' in your project directory to get started."
Write-Host "========================================="
