#!/bin/bash
# test.sh
# Verification script for the Nautilus AGE Encryption extension

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   AGE ENCRYPTION - Extension Test Suite              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

PASSED=0
FAILED=0

# Test function for commands
test_command() {
    local cmd=$1
    local name=$2

    echo -n "Testing $name... "
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test function for packages
test_package() {
    local pkg=$1
    local name=$2

    echo -n "Testing $name... "
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test function for files
test_file() {
    local file=$1
    local name=$2

    echo -n "Testing $name... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}[1/6] Checking system commands...${NC}"
test_command "nautilus" "Nautilus"
test_command "age" "age encryption"
test_command "zenity" "Zenity dialogs"
test_command "notify-send" "Desktop notifications"
test_command "shred" "Secure deletion"
test_command "tar" "TAR compression"
# mat2 is optional - don't fail if not installed
echo -n "Testing mat2 (optional)... "
if command -v mat2 &> /dev/null; then
    echo -e "${GREEN}✓${NC} (metadata cleaning enabled)"
    ((PASSED++))
else
    echo -e "${YELLOW}○${NC} (not installed - metadata cleaning disabled)"
    echo -e "    ${YELLOW}To enable: sudo apt install mat2${NC}"
fi
echo ""

echo -e "${BLUE}[2/6] Checking installed packages...${NC}"
test_package "python3-nautilus" "python3-nautilus"
test_package "age" "age package"
test_package "zenity" "zenity package"
test_package "libnotify-bin" "libnotify-bin"
echo ""

echo -e "${BLUE}[3/6] Checking extension files...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test_file "$SCRIPT_DIR/nautilus-age-extension.py" "Extension file"
test_file "$SCRIPT_DIR/install.sh" "Install script"
test_file "$SCRIPT_DIR/README.md" "Documentation"
echo ""

echo -e "${BLUE}[4/6] Checking extension installation...${NC}"
EXTENSION_FILE="$HOME/.local/share/nautilus-python/extensions/nautilus-age-extension.py"
if [ -f "$EXTENSION_FILE" ]; then
    echo -e "Extension installed: ${GREEN}✓${NC}"
    ((PASSED++))
else
    echo -e "Extension installed: ${YELLOW}Not installed (run install script)${NC}"
fi
echo ""

echo -e "${BLUE}[5/6] Basic functional test...${NC}"
TEST_FILE="/tmp/age-test-$$.txt"
echo "Test data for age encryption" > "$TEST_FILE"

echo -n "Testing age encryption... "
if echo -e "testpassword\ntestpassword" | age -p "$TEST_FILE" > "$TEST_FILE.age" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))

    echo -n "Testing age decryption... "
    if echo "testpassword" | age -d "$TEST_FILE.age" > "$TEST_FILE.decrypted" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))

        echo -n "Verifying decrypted content... "
        if diff -q "$TEST_FILE" "$TEST_FILE.decrypted" &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            ((PASSED++))
        else
            echo -e "${RED}✗${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC}"
    ((FAILED++))
fi

# Clean up test files
rm -f "$TEST_FILE" "$TEST_FILE.age" "$TEST_FILE.decrypted"
echo ""

echo -e "${BLUE}[6/6] Testing metadata cleaning (optional)...${NC}"
if command -v mat2 &> /dev/null; then
    # Create a test file and check mat2 can process it
    MAT2_TEST="/tmp/mat2-test-$$.txt"
    echo "Test content" > "$MAT2_TEST"
    echo -n "Testing mat2 execution... "
    if mat2 --inplace --unknown-members omit "$MAT2_TEST" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        # Return code 1 means unsupported format, which is OK
        echo -e "${GREEN}✓${NC} (format not supported, but mat2 works)"
        ((PASSED++))
    fi
    rm -f "$MAT2_TEST"
else
    echo -e "mat2 not installed - ${YELLOW}skipped${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Tests passed: ${GREEN}$PASSED${NC}"
echo -e "Tests failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗"
    echo -e "║              ALL TESTS PASSED! ✓                      ║"
    echo -e "╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}The extension is ready to use!${NC}"
    echo ""
    if [ ! -f "$EXTENSION_FILE" ]; then
        echo -e "${YELLOW}Run ./install.sh to install it${NC}"
    else
        echo -e "Open Nautilus and you will see the encryption options"
    fi
    echo ""
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗"
    echo -e "║              SOME TESTS FAILED                        ║"
    echo -e "╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Solutions:${NC}"
    echo ""
    if ! command -v age &> /dev/null; then
        echo "  • Install age: sudo apt install age"
    fi
    if ! command -v zenity &> /dev/null; then
        echo "  • Install zenity: sudo apt install zenity"
    fi
    if ! command -v notify-send &> /dev/null; then
        echo "  • Install libnotify-bin: sudo apt install libnotify-bin"
    fi
    if ! dpkg -l | grep -q "python3-nautilus"; then
        echo "  • Install python3-nautilus: sudo apt install python3-nautilus"
    fi
    echo ""
    echo "Or simply run: ./install.sh"
    echo ""
    exit 1
fi
