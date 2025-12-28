# 🔐 AGE Encryption - Nautilus Extension

Complete Nautilus (GNOME Files) extension for encrypting and decrypting files using **age** (Actually Good Encryption).

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

## 📋 Features

### ✨ Main Functionalities

- **🔒 Encrypt individual files** - Right-click → Encrypt with age
- **🔓 Decrypt .age files** - Right-click on .age files → Decrypt with age
- **📦 Encrypt complete folders** - Compresses (tar.gz) and encrypts in a single step
- **🎲 Passphrase generator** - Generate secure, memorable passphrases with one click
- **🗑️ Optional secure deletion** - Deletes original files with `shred` (3 passes)
- **✅ Integrity verification** - Validates .age files before decryption
- **🔄 Batch encryption** - Select multiple files and encrypt all at once
- **📦 Automatic extraction** - Decompresses encrypted folders automatically
- **🔔 Notifications** - System notifications when operations complete
- **🎨 Intuitive interface** - Native GTK dialogs with passphrase generation
- **🧹 Auto metadata cleaning** - Automatically removes EXIF, author, dates (originals preserved)

### 🛡️ Security

- **Algorithm:** ChaCha20-Poly1305 (same used by Google, Cloudflare, WireGuard)
- **Key derivation:** scrypt (resistant to GPU/ASIC attacks)
- **Authentication:** Built-in (detects modifications)
- **No dangerous configuration:** age is designed to be secure by default
- **🚫 Rate limiting:** Protection against brute-force attacks (3 attempts, 30s lockout)
- **🛤️ Path validation:** Protection against path traversal attacks
- **📝 Logging system:** Security events logged for audit

## 📸 Screenshots

### Encrypt a file
![Encrypt file context menu](screenshots/01.png)

### Encrypt a folder
![Encrypt folder context menu](screenshots/03.png)

### Decrypt a file
![Decrypt file context menu](screenshots/04.png)

### Encrypted vs Original file
![Encrypted file comparison](screenshots/02.png)

## 📦 Requirements

### Operating System
- Debian 13+ (Trixie) or Debian 14+
- Ubuntu 24.04+ (Noble) or higher
- Any distribution with GNOME/Nautilus

### Dependencies
All are installed automatically:
- `python3-nautilus` - Python bindings for Nautilus
- `age` - Encryption tool
- `zenity` - Graphical dialogs
- `libnotify-bin` - System notifications
- `coreutils` - Basic utilities (includes `shred`)

### Optional Dependencies
- `mat2` - Metadata cleaning tool (for privacy-focused encryption)

## 🚀 Installation

### Method 1: Automatic installation (recommended)

```bash
# 1. Download the files
git clone https://github.com/your-username/age-nautilus-extension.git
cd age-nautilus-extension

# 2. Run the installer
chmod +x install-age-nautilus.sh
./install-age-nautilus.sh
```

Done! The extension is now installed and working.

### Method 2: Manual installation

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3-nautilus age zenity libnotify-bin

# 2. Create extensions directory
mkdir -p ~/.local/share/nautilus-python/extensions

# 3. Copy the extension
cp age-nautilus-extension.py ~/.local/share/nautilus-python/extensions/
chmod +x ~/.local/share/nautilus-python/extensions/age-nautilus-extension.py

# 4. Restart Nautilus
nautilus -q
```

## 📖 Usage

### Encrypt a file

1. Open Nautilus (GNOME Files)
2. Navigate to your file
3. **Right-click** → **"Encrypt with age"**
4. A secure 24-word passphrase is generated and copied to clipboard
5. **Save the passphrase** in a password manager
6. Click **Encrypt** - optionally delete the original
7. ✅ Creates `file.ext.age`

### Encrypt multiple files

1. **Select multiple files** (Ctrl + Click)
2. **Right-click** → **"Encrypt N files with age"**
3. Save the generated passphrase
4. All files are encrypted with the same passphrase

### Encrypt a complete folder

1. **Right-click on a folder** → **"Encrypt folder with age"**
2. Save the generated passphrase
3. Creates `folder.tar.gz.age` (compressed and encrypted)
4. Optionally, accept deleting the original folder

### Decrypt files

1. **Right-click on .age file** → **"Decrypt with age"**
2. Enter your passphrase
3. Original file is recovered
4. If it's a folder (`.tar.gz`), it's automatically extracted

### 🎲 Secure Passphrase (Automatic)

When encrypting files or folders, a **secure passphrase is automatically generated** - no manual passwords allowed for maximum security:

1. Right-click and select **"Encrypt with age"**
2. A secure 24-word passphrase is generated automatically
3. The passphrase is **automatically copied to clipboard**
4. **SAVE IT NOW** in a password manager before clicking Encrypt

**Security features:**
- **Cryptographically secure**: Uses Python `secrets` module (CSPRNG)
- **24 words**: ~215 bits of entropy - impossible to brute-force
- **No weak passwords**: Manual entry disabled - can't use "123456"
- **One-click flow**: No need to type or confirm anything

**The passphrase dialog shows:**
```
📋 Passphrase copied to clipboard!

tiger-ocean-mountain-castle-brave-silent-...

⚠️ Save this passphrase now!

[🔒 Encrypt]    [Cancel]
```

### 🧹 Automatic Metadata Cleaning

When `mat2` is installed, metadata is **automatically cleaned** before encryption:

- **No prompts needed** - cleaning happens silently in the background
- **Original files preserved** - metadata is cleaned from temporary copies only
- **Encrypted output** - the `.age` file contains metadata-free content
- **Your originals are safe** - they keep all their metadata untouched

**What gets cleaned:**
- **Photos**: EXIF data (GPS location, camera model, timestamps)
- **Documents**: Author name, company, creation/modification dates
- **PDFs**: Metadata, comments, revision history
- **Audio**: ID3 tags, artist, album information
- **Video**: Creation dates, camera info, GPS

**Supported formats** (via mat2):
- Images: JPEG, PNG, GIF, BMP, TIFF
- Documents: DOCX, XLSX, PPTX, ODT, ODS, ODP
- PDFs: PDF files
- Audio: MP3, FLAC, OGG
- Video: MP4, AVI, MKV
- Archives: ZIP, TAR

**Requirements:**
- `mat2` must be installed: `sudo apt install mat2`
- If not installed, encryption proceeds without metadata cleaning (no warning)

**Why clean metadata?**
- Photos can reveal your location (GPS), camera, and when they were taken
- Documents often contain your name, company, and edit history
- Cleaning metadata protects your privacy when sharing encrypted files

## 🎯 Use Case Examples

### Case 1: Confidential documents

```
secret-document.pdf
→ Encrypt with age
→ secret-document.pdf.age (encrypted)
→ Delete original ✓
```

### Case 2: Complete project backup

```
my-project/
  ├── code/
  ├── documentation/
  └── data/

→ Encrypt folder with age
→ my-project.tar.gz.age (everything compressed and encrypted)
```

### Case 3: Sharing encrypted files

```
1. Encrypt: photo.jpg → photo.jpg.age
2. Share photo.jpg.age via email/USB
3. Share password through another channel (Signal, phone call)
4. Recipient: Right-click → Decrypt with age
```

## 🔧 Advanced Configuration

### Change number of shred passes

Edit `age-nautilus-extension.py`:

```python
# Line ~565
subprocess.run(['shred', '-vfzu', '-n', '35', file_path])  # 35 passes (Gutmann)
```

### Disable secure deletion

Comment these lines in the `on_encrypt_files` method:

```python
# if delete_originals:
#     self.secure_delete(file_path)
```

## 🐛 Troubleshooting

### Extension doesn't appear in Nautilus

```bash
# Verify python3-nautilus is installed
dpkg -l | grep python3-nautilus

# Verify extension is in the right place
ls -la ~/.local/share/nautilus-python/extensions/

# Restart Nautilus
nautilus -q
killall nautilus
nautilus &
```

### Error: "age is not installed"

```bash
# Install age
sudo apt install age

# Verify installation
age --version
```

### Dialogs don't appear

```bash
# Verify zenity
which zenity

# If not installed
sudo apt install zenity
```

### Notifications don't work

```bash
# Verify notify-send
which notify-send

# If not installed
sudo apt install libnotify-bin
```

### Permission error

```bash
# Grant execution permissions
chmod +x ~/.local/share/nautilus-python/extensions/age-nautilus-extension.py
```

## 🔐 Security and Best Practices

### Strong passwords

✅ **GOOD:**
- `correct-horse-battery-staple-2024-secure`
- `Tr0ub4dor&3-MySecretP@ssw0rd!`
- Minimum 20 characters
- Mix of words, numbers, symbols

❌ **BAD:**
- `password123`
- `qwerty`
- Your name
- Short passwords

### Sharing encrypted files

1. **NEVER** send the .age file and password through the same channel
2. .age file → Email/USB
3. Password → Signal/Phone call/SMS
4. For maximum security: share password in person

### File verification

The extension automatically verifies that .age files are valid before attempting to decrypt them.

### Secure deletion

- `shred` overwrites the file 3 times
- Makes forensic recovery nearly impossible
- Only useful on HDD drives (not on SSD/NVMe due to wear leveling)

## 📊 Comparison with Other Solutions

| Feature | age-nautilus | GPG-Nautilus | Veracrypt | zip -e |
|---------|-------------|--------------|-----------|--------|
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Security | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| GUI Integration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Modern | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |

## 🗑️ Uninstallation

```bash
# Remove the extension
rm ~/.local/share/nautilus-python/extensions/age-nautilus-extension.py

# Restart Nautilus
nautilus -q

# Optional: uninstall dependencies
sudo apt remove python3-nautilus age zenity
```

## 🤝 Contributing

Found a bug? Have an idea for improvement?

1. Fork the repository
2. Create a branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -am 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Open a Pull Request

## 📝 Changelog

### v1.4.0 (2025-12-28)
- 🔐 **Passphrase Only**: Removed manual password option - only auto-generated passphrases allowed
- 📋 **Improved Clipboard UI**: Clear message "Passphrase copied to clipboard!" with save instructions
- 🛡️ **Maximum Security**: Impossible to use weak passwords - always 24-word passphrase (~215 bits)
- ⚡ **Simpler Flow**: One-click encryption without password confirmation dialogs
- ✅ **Security Verified**: mat2 execution confirmed secure (no shell injection possible)
- 🧹 **Clean Menus**: Removed emojis from context menu items for cleaner UI
- 📦 **Auto-Extract Folders**: Encrypted folders (.tar.gz) are automatically extracted on decryption
- 💬 **Compact UI**: Shortened warning messages for cleaner dialog appearance

### v1.3.0 (2025-12-28)
- 🧹 **Automatic Metadata Cleaning**: Silently removes EXIF, author, dates, GPS before encryption
- 🔒 **Originals Preserved**: Cleans temporary copies only - your files keep their metadata
- 📦 **Folder Support**: Recursively clean all files in a folder before compression
- ⚡ **Zero Prompts**: No questions asked - if mat2 is installed, cleaning is automatic
- 🛡️ **Path Validation**: All cleaned files validated for security

### v1.2.0 (2025-12-28)
- 🛡️ **Security Audit**: Complete security review with Semgrep - 0 vulnerabilities
- 🚫 **Rate Limiting**: Brute-force protection (3 attempts per file, 30s lockout, 5min window)
- 🛤️ **Path Validation**: Protection against path traversal attacks and accidental system damage
- 📝 **Logging System**: Security events logged via Python `logging` module
- 🔄 **Safe Deletion**: Replaced `rm -rf` with `shutil.rmtree()` + validation
- 🏷️ **Type Hints**: Full type annotations for better code quality
- 🐛 **Bug Fixes**: Fixed GLib return values for proper async handling

### v1.1.0 (2025-12-28)
- 🎲 **Passphrase Generator**: Generate secure, memorable passphrases with one click
- 📋 **Auto-copy to clipboard**: Generated passphrases are automatically copied
- 🎨 **Native GTK dialogs**: Replaced Zenity password dialogs with native GTK for better integration
- ⚡ **Skip confirmation**: Generated passphrases skip the re-enter step for faster workflow
- 🔒 Uses cryptographically secure `secrets` module for random selection

### v1.0.0 (2025-12-27)
- ✨ Initial release
- 🔒 Individual file encryption
- 📦 Complete folder encryption
- 🔓 Decryption with verification
- 🗑️ Optional secure deletion
- 🔔 System notifications
- 🎨 Intuitive UI with Zenity

## 📄 License

MIT License - See LICENSE file for details

## 👏 Credits

- **Author** - Homero Thompson del Lago del Terror
- **age** - Filippo Valsorda (Google Crypto Team)
- **Nautilus** - GNOME Project

## 🔗 Useful Links

- [age GitHub](https://github.com/FiloSottile/age)
- [age Documentation](https://age-encryption.org/)
- [Nautilus Python](https://wiki.gnome.org/Projects/NautilusPython)
- [age Specification](https://c2sp.org/age)

---

**Found it useful?** ⭐ Star the repository!

**Questions?** Open an issue on GitHub

**Secure encryption for everyone! 🔐**
