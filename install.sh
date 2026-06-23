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

# 4. Make sure the 'aim' command is reachable. pip often installs console
#    scripts into a folder (e.g. ~/.local/bin) that is not on PATH, which is
#    why 'aim' can be "command not found" right after install. Locate it and
#    optionally add it to PATH. From here on, don't abort on minor errors -
#    the install itself already succeeded.
set +e

# Find the folder where the 'aim' executable landed.
AIM_DIR=""
if command -v aim &>/dev/null; then
    AIM_DIR="$(dirname "$(command -v aim)")"
else
    CANDIDATES="$($PYTHON_CMD -c 'import sysconfig
seen = []
try:
    seen.append(sysconfig.get_paths("posix_user")["scripts"])
except Exception:
    pass
try:
    seen.append(sysconfig.get_path("scripts"))
except Exception:
    pass
print("\n".join([p for p in seen if p]))')"
    while IFS= read -r d; do
        [ -z "$d" ] && continue
        if [ -x "$d/aim" ]; then AIM_DIR="$d"; break; fi
        [ -z "$AIM_DIR" ] && AIM_DIR="$d"
    done <<< "$CANDIDATES"
fi

# Is AIM_DIR already on PATH?
on_path() {
    case ":$PATH:" in
        *":$1:"*) return 0 ;;
        *) return 1 ;;
    esac
}

if [ -z "$AIM_DIR" ]; then
    echo "[!] Could not locate the 'aim' executable automatically."
    echo "    You can still run it with:  $PYTHON_CMD -m aim.aim_cli init"
elif on_path "$AIM_DIR"; then
    echo "[+] 'aim' is on your PATH - you can run it directly."
else
    echo "[!] The 'aim' command was installed to:"
    echo "      $AIM_DIR"
    echo "    but this folder is NOT on your PATH, so typing 'aim' won't work yet."
    echo ""

    # Pick the right shell startup file.
    SHELL_NAME="$(basename "${SHELL:-bash}")"
    case "$SHELL_NAME" in
        zsh)  RC_FILE="$HOME/.zshrc" ;;
        bash)
            if [ "$(uname)" = "Darwin" ]; then RC_FILE="$HOME/.bash_profile"; else RC_FILE="$HOME/.bashrc"; fi
            ;;
        *)    RC_FILE="$HOME/.profile" ;;
    esac

    DO_ADD="n"
    # Open the real terminal on fd 3. This both tests interactivity and lets us
    # read the answer even when the script itself arrived via `curl | bash`
    # (where stdin is the pipe, not the keyboard). If /dev/tty can't be opened
    # we are non-interactive: do NOT touch PATH, just print instructions.
    if { exec 3</dev/tty; } 2>/dev/null; then
        printf "Add this folder to your PATH in %s now? [Y/n] (Enter = Yes, type n to skip) " "$RC_FILE"
        read -r ANSWER <&3 || ANSWER=""
        exec 3<&-
        case "$ANSWER" in
            ""|[Yy]|[Yy][Ee][Ss]) DO_ADD="y" ;;
        esac
    else
        echo "[*] Non-interactive session detected; not changing PATH automatically."
    fi

    if [ "$DO_ADD" = "y" ]; then
        if [ -f "$RC_FILE" ] && grep -Fq "$AIM_DIR" "$RC_FILE"; then
            echo "[+] $RC_FILE already references this folder."
        else
            printf '\n# Added by AIM installer\nexport PATH="$PATH:%s"\n' "$AIM_DIR" >> "$RC_FILE"
            echo "[+] Added to $RC_FILE"
        fi
        export PATH="$PATH:$AIM_DIR"
        echo "[+] Updated PATH for this session."
        echo "    Open a new terminal, or run:  source $RC_FILE"
    else
        echo ""
        echo "To add it later, run:"
        echo "  echo 'export PATH=\"\$PATH:$AIM_DIR\"' >> $RC_FILE && source $RC_FILE"
        echo ""
        echo "Or run AIM without changing PATH:"
        echo "  $PYTHON_CMD -m aim.aim_cli init"
    fi
fi

echo ""
echo "Get started:"
echo "  aim init        # run inside your project directory"
echo "  aim --help"
echo "========================================="
