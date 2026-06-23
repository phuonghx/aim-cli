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

# 4. Make sure the 'aim' command is reachable (fix the classic
#    "'aim' is not recognized..." problem) by locating the Scripts folder
#    where pip placed aim.exe and optionally adding it to the user PATH.

function Get-AimScriptDir {
    param([string]$PythonCmd)

    # If 'aim' already resolves, use its real folder.
    $cmd = Get-Command aim -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) { return (Split-Path -Parent $cmd.Source) }

    # Ask Python where console scripts are installed (user scheme first, then global).
    $pyCode = @'
import sysconfig
dirs = []
for scheme in ("nt_user", "nt"):
    try:
        d = sysconfig.get_paths(scheme).get("scripts")
        if d:
            dirs.append(d)
    except Exception:
        pass
for d in dirs:
    print(d)
'@
    # Pipe the code via stdin (python -) rather than `-c "<code>"`: Windows
    # PowerShell 5.1 strips embedded double quotes when passing arguments to
    # native exes, which turns "nt_user"/"nt" into bare names and crashes with
    # NameError. stdin sidesteps command-line quoting entirely.
    $candidates = $pyCode | & $PythonCmd -

    # Prefer a folder that actually contains aim.exe.
    foreach ($d in $candidates) {
        if ($d -and (Test-Path (Join-Path $d 'aim.exe'))) { return $d }
    }
    if ($candidates) { return ($candidates | Select-Object -First 1) }
    return $null
}

function Test-OnPath {
    param([string]$Dir)
    if (-not $Dir) { return $false }
    $norm = $Dir.TrimEnd('\').ToLowerInvariant()
    foreach ($p in ($env:Path -split ';')) {
        if ($p -and ($p.TrimEnd('\').ToLowerInvariant() -eq $norm)) { return $true }
    }
    return $false
}

$scriptDir = Get-AimScriptDir -PythonCmd $pythonCmd

if (Test-OnPath $scriptDir) {
    Write-Host "[+] 'aim' is on your PATH - you can run it directly." -ForegroundColor Green
}
elseif ($scriptDir) {
    Write-Host "[!] The 'aim' command was installed to:" -ForegroundColor Yellow
    Write-Host "      $scriptDir" -ForegroundColor Yellow
    Write-Host "    but this folder is NOT on your PATH, so typing 'aim' won't work yet." -ForegroundColor Yellow
    Write-Host ""

    $doAdd = $false
    $canPrompt = -not [Console]::IsInputRedirected
    if ($canPrompt) {
        try {
            $answer = Read-Host "Add this folder to your user PATH now? [Y/n] (Enter = Yes, type n to skip)"
            $answer = "$answer".Trim()
            if ($answer -eq '' -or $answer -match '^(y|yes)$') { $doAdd = $true }
        } catch {
            $canPrompt = $false
        }
    }
    if (-not $canPrompt) {
        Write-Host "[*] Non-interactive session detected; not changing PATH automatically." -ForegroundColor DarkGray
    }

    if ($doAdd) {
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        $already = $false
        if ($userPath) {
            foreach ($p in ($userPath -split ';')) {
                if ($p -and ($p.TrimEnd('\').ToLowerInvariant() -eq $scriptDir.TrimEnd('\').ToLowerInvariant())) {
                    $already = $true; break
                }
            }
        }
        if (-not $already) {
            $newPath = if ([string]::IsNullOrEmpty($userPath)) { $scriptDir } else { ($userPath.TrimEnd(';') + ';' + $scriptDir) }
            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            Write-Host "[+] Added to your user PATH." -ForegroundColor Green
        } else {
            Write-Host "[+] Already present in your user PATH." -ForegroundColor Green
        }
        # Update the current window too, so 'aim' works right away here.
        $env:Path = "$env:Path;$scriptDir"
        Write-Host "[+] Updated PATH for THIS window. Open a NEW terminal for it to apply everywhere." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "To add it later, paste this into PowerShell:" -ForegroundColor Cyan
        Write-Host "  `$d = '$scriptDir'" -ForegroundColor White
        Write-Host "  [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User').TrimEnd(';') + ';' + `$d, 'User')" -ForegroundColor White
        Write-Host "  # then close and reopen your terminal" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "Or run AIM without touching PATH:" -ForegroundColor Cyan
        Write-Host "  $pythonCmd -m aim.aim_cli init" -ForegroundColor White
    }
}
else {
    Write-Host "[!] Could not locate the 'aim' executable automatically." -ForegroundColor Yellow
    Write-Host "    You can still run it with:  $pythonCmd -m aim.aim_cli init" -ForegroundColor White
}

Write-Host ""
Write-Host "Get started:" -ForegroundColor Cyan
Write-Host "  aim init        # run inside your project directory" -ForegroundColor White
Write-Host "  aim --help" -ForegroundColor White
Write-Host "========================================="
