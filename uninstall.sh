#!/bin/bash
# uninstall.sh
# Uninstallation script for the Nautilus AGE Encryption extension

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   AGE ENCRYPTION - Nautilus Extension Uninstaller    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

EXTENSION_FILE="$HOME/.local/share/nautilus-python/extensions/nautilus-age-extension.py"

# Check if extension is installed
if [ ! -f "$EXTENSION_FILE" ]; then
    echo -e "${YELLOW}[!]${NC} The extension is not installed"
    exit 0
fi

# Confirm uninstallation
echo -e "${YELLOW}[!]${NC} This will remove the AGE Encryption extension from Nautilus"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[*]${NC} Uninstallation cancelled"
    exit 0
fi

# Remove extension
echo -e "${BLUE}[*]${NC} Removing extension..."
rm -f "$EXTENSION_FILE"
echo -e "${GREEN}[✓]${NC} Extension removed"

# Restart Nautilus
echo -e "${BLUE}[*]${NC} Restarting Nautilus..."
nautilus -q 2>/dev/null || true
sleep 1
echo -e "${GREEN}[✓]${NC} Nautilus restarted"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗"
echo -e "║       UNINSTALLATION COMPLETED SUCCESSFULLY           ║"
echo -e "╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}[*]${NC} The extension has been removed"
echo -e "${BLUE}[*]${NC} Dependencies (age, zenity, etc.) have NOT been removed"
echo ""
echo -e "${YELLOW}To also remove dependencies:${NC}"
echo "  sudo apt remove age zenity libnotify-bin python3-nautilus"
echo ""
echo -e "${GREEN}Thank you for using AGE Encryption!${NC} 🔐"
echo ""
