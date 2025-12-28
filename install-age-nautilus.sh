#!/bin/bash
# install-age-nautilus.sh
# Installation script for the age Nautilus extension
#
# Usage: ./install-age-nautilus.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   AGE ENCRYPTION - Nautilus Extension Installer      ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Verify running on Debian/Ubuntu
if ! command -v apt &> /dev/null; then
    print_error "This script is designed for Debian/Ubuntu"
    exit 1
fi

print_status "Checking system..."

# Verify we are in a GNOME/Nautilus environment
if ! command -v nautilus &> /dev/null; then
    print_error "Nautilus (GNOME Files) is not installed"
    print_warning "Install GNOME first: sudo apt install nautilus"
    exit 1
fi

print_success "Nautilus detected"

# Check dependencies
print_status "Checking dependencies..."

MISSING_DEPS=()

if ! dpkg -l | grep -q "python3-nautilus"; then
    MISSING_DEPS+=("python3-nautilus")
fi

if ! command -v age &> /dev/null; then
    MISSING_DEPS+=("age")
fi

if ! command -v zenity &> /dev/null; then
    MISSING_DEPS+=("zenity")
fi

if ! command -v notify-send &> /dev/null; then
    MISSING_DEPS+=("libnotify-bin")
fi

if ! command -v shred &> /dev/null; then
    MISSING_DEPS+=("coreutils")
fi

if ! command -v mat2 &> /dev/null; then
    MISSING_DEPS+=("mat2")
fi

# Install missing dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_warning "Missing dependencies: ${MISSING_DEPS[*]}"
    print_status "Installing dependencies..."

    sudo apt update
    sudo apt install -y "${MISSING_DEPS[@]}"

    print_success "Dependencies installed"
else
    print_success "All dependencies are installed"
fi

# Create Nautilus extension directory if it doesn't exist
EXTENSION_DIR="$HOME/.local/share/nautilus-python/extensions"
print_status "Creating extension directory..."
mkdir -p "$EXTENSION_DIR"
print_success "Directory created: $EXTENSION_DIR"

# Copy the extension
print_status "Installing extension..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/age-nautilus-extension.py" ]; then
    cp "$SCRIPT_DIR/age-nautilus-extension.py" "$EXTENSION_DIR/"
    chmod +x "$EXTENSION_DIR/age-nautilus-extension.py"
    print_success "Extension installed at: $EXTENSION_DIR/age-nautilus-extension.py"
else
    print_error "age-nautilus-extension.py not found"
    print_error "Make sure to run this script from the correct directory"
    exit 1
fi

# Restart Nautilus
print_status "Restarting Nautilus..."
nautilus -q 2>/dev/null || true
sleep 2
print_success "Nautilus restarted"

# Final message
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗"
echo -e "║            INSTALLATION COMPLETE! 🎉                   ║"
echo -e "╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
print_success "The AGE Encryption extension is ready to use"
echo ""
echo -e "${BLUE}How to use:${NC}"
echo "  1. Open Nautilus (GNOME Files)"
echo "  2. Right-click on any file"
echo "  3. You will see new options:"
echo "     • Encrypt with age         (encrypt file)"
echo "     • Encrypt folder with age  (encrypt entire folder)"
echo "     • Decrypt with age         (decrypt .age file)"
echo ""
echo -e "${BLUE}Features included:${NC}"
echo "  ✓ Encryption with ChaCha20-Poly1305 (state of the art)"
echo "  ✓ Encrypt multiple files at once"
echo "  ✓ Encrypt complete folders (tar.gz + age)"
echo "  ✓ Secure deletion of original files (3 passes)"
echo "  ✓ Automatic integrity verification"
echo "  ✓ Automatic folder decompression"
echo "  ✓ System notifications"
echo "  ✓ Native GTK dialogs"
echo "  ✓ Passphrase generator (one-click secure passwords)"
echo "  ✓ Metadata cleaning before encryption (requires mat2)"
echo ""
echo -e "${BLUE}Security features (v1.2.0):${NC}"
echo "  ✓ Rate limiting (brute-force protection)"
echo "  ✓ Path validation (traversal attack protection)"
echo "  ✓ Security logging system"
echo ""
echo -e "${BLUE}Privacy features (v1.3.0):${NC}"
echo "  ✓ Metadata cleaning with mat2"
echo ""
echo -e "${BLUE}New in v1.4.0:${NC}"
echo "  ✓ Auto-generated 24-word passphrases (~215 bits entropy)"
echo "  ✓ No manual passwords - maximum security by default"
echo "  ✓ Auto-copy passphrase to clipboard"
echo "  ✓ Auto-extract encrypted folders on decryption"
echo ""
echo -e "${YELLOW}Security note:${NC}"
echo "  • Passphrases are generated automatically (24 words)"
echo "  • age uses scrypt key derivation (brute-force resistant)"
echo "  • .age files are protected with ChaCha20-Poly1305"
echo ""
echo -e "${BLUE}To uninstall:${NC}"
echo "  rm $EXTENSION_DIR/age-nautilus-extension.py"
echo "  nautilus -q"
echo ""
print_success "Enjoy secure encryption with age! 🔐"
echo ""
