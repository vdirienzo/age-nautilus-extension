#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGE Encryption Extension for Nautilus
======================================
Nautilus extension for encrypting/decrypting files with age (Actually Good Encryption)

Features:
- Encrypt individual files
- Encrypt multiple files at once
- Encrypt complete folders (tar.gz + age)
- Decrypt .age files
- Secure deletion of original file (optional)
- Integrity verification before decrypting
- System notifications

Author: Homero Thompson del Lago del Terror
Date: December 2025
License: MIT
"""

import logging
import os
import pty
import secrets
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Dict, List, Optional, Tuple

# Configure logging for the extension
logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger('age-nautilus')

# Rate limiting constants
RATE_LIMIT_MAX_ATTEMPTS = 3
RATE_LIMIT_LOCKOUT_SECONDS = 30
RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes

# Detect available Nautilus version
# IMPORTANT: DO NOT use exit() - it crashes Nautilus
from gi import require_version

NAUTILUS_VERSION = None
_import_error = None

# Try Nautilus 4.1 (Debian 13/Trixie, Ubuntu 24.04+)
try:
    require_version('Nautilus', '4.1')
    require_version('Gtk', '4.0')
    require_version('Gdk', '4.0')
    from gi.repository import Nautilus, GObject, Gtk, Gio, Gdk, GLib
    NAUTILUS_VERSION = 4
except (ValueError, ImportError):
    pass

# Try Nautilus 4.0 (older versions)
if NAUTILUS_VERSION is None:
    try:
        require_version('Nautilus', '4.0')
        require_version('Gtk', '4.0')
        require_version('Gdk', '4.0')
        from gi.repository import Nautilus, GObject, Gtk, Gio, Gdk, GLib
        NAUTILUS_VERSION = 4
    except (ValueError, ImportError):
        pass

# Try Nautilus 3.0 (legacy)
if NAUTILUS_VERSION is None:
    try:
        require_version('Nautilus', '3.0')
        require_version('Gtk', '3.0')
        require_version('Gdk', '3.0')
        from gi.repository import Nautilus, GObject, Gtk, Gio, Gdk, GLib
        NAUTILUS_VERSION = 3
    except (ValueError, ImportError) as e:
        _import_error = e

# If no version could be imported, create dummy class to avoid crash
if NAUTILUS_VERSION is None:
    logger.error(f"Could not import Nautilus: {_import_error}")
    logger.error("Extension will not be available.")
    # Create dummy classes so the file loads without error
    class GObject:
        class GObject:
            pass
    class Nautilus:
        class MenuProvider:
            pass
        class MenuItem:
            def __init__(self, **kwargs): pass
            def connect(self, *args): pass


# Wordlist for passphrase generation (~500 common English words, 4-8 letters)
# Based on EFF's diceware wordlist for memorable passphrases
PASSPHRASE_WORDLIST = [
    "about", "above", "acid", "actor", "adopt", "adult", "after", "again",
    "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "alive",
    "alley", "allow", "alone", "alpha", "alter", "amino", "among", "ample",
    "angel", "anger", "angle", "angry", "ankle", "apart", "apple", "apply",
    "arena", "argue", "armor", "arrow", "aside", "asset", "atlas", "audio",
    "audit", "avoid", "award", "bacon", "badge", "badly", "baker", "bases",
    "basic", "basin", "basis", "batch", "beach", "beard", "beast", "began",
    "begin", "begun", "being", "belly", "below", "bench", "berry", "bible",
    "bikes", "birds", "birth", "black", "blade", "blame", "blank", "blast",
    "blaze", "bleed", "blend", "bless", "blind", "blink", "block", "blood",
    "bloom", "blown", "blues", "blunt", "board", "boast", "boats", "bored",
    "bonus", "boost", "booth", "boots", "bound", "boxer", "brain", "brand",
    "brass", "brave", "bread", "break", "breed", "brick", "bride", "brief",
    "bring", "brisk", "broad", "broke", "brook", "brown", "brush", "build",
    "built", "bunch", "burst", "cabin", "cable", "camel", "canal", "candy",
    "canoe", "cards", "cargo", "carry", "carve", "catch", "cause", "cease",
    "cedar", "chain", "chair", "chalk", "champ", "chaos", "charm", "chart",
    "chase", "cheap", "check", "cheek", "chess", "chest", "chief", "child",
    "chill", "china", "chips", "chord", "chose", "chunk", "civic", "civil",
    "claim", "clash", "class", "clean", "clear", "clerk", "click", "cliff",
    "climb", "cling", "cloak", "clock", "clone", "close", "cloth", "cloud",
    "clown", "clubs", "coach", "coast", "codes", "comet", "comic", "coral",
    "could", "count", "coupe", "court", "cover", "crack", "craft", "crane",
    "crash", "crawl", "crazy", "cream", "creek", "creep", "crest", "crime",
    "crisp", "cross", "crowd", "crown", "crude", "cruel", "crush", "cubic",
    "curve", "cycle", "daily", "dairy", "dance", "darts", "dealt", "death",
    "debut", "decal", "decay", "decor", "decoy", "delta", "demon", "denim",
    "dense", "depot", "depth", "derby", "desks", "devil", "diary", "digit",
    "diner", "dirty", "disco", "ditch", "diver", "dodge", "doing", "donor",
    "doubt", "dough", "downs", "dozen", "draft", "drain", "drake", "drama",
    "drank", "drape", "drawl", "drawn", "dream", "dress", "dried", "drift",
    "drill", "drink", "drive", "droit", "drown", "drugs", "drums", "drunk",
    "dusty", "dwarf", "eager", "eagle", "early", "earth", "easel", "eaten",
    "eaves", "ebony", "edges", "eight", "elbow", "elder", "elect", "elite",
    "empty", "ended", "enemy", "enjoy", "enter", "entry", "equal", "equip",
    "error", "erupt", "essay", "evade", "event", "every", "exact", "exams",
    "excel", "exile", "exist", "extra", "fable", "facts", "faint", "fairy",
    "faith", "false", "fancy", "fatal", "fault", "favor", "feast", "fence",
    "ferry", "fetch", "fever", "fiber", "field", "fifth", "fifty", "fight",
    "films", "final", "finds", "fired", "firms", "first", "fixed", "flags",
    "flame", "flank", "flash", "flask", "flock", "flood", "floor", "flora",
    "flour", "fluid", "flush", "flute", "focal", "focus", "foggy", "folks",
    "force", "forge", "forms", "forth", "forum", "fossil", "found", "frame",
    "frank", "fraud", "fresh", "fried", "front", "frost", "fruit", "fully",
    "funds", "funny", "fused", "gains", "gamma", "gauge", "gears", "geese",
    "genre", "ghost", "giant", "gifts", "girls", "given", "gives", "gland",
    "glass", "gleam", "glide", "globe", "glory", "gloss", "glove", "glyph",
    "goals", "goats", "going", "goods", "goose", "grace", "grade", "grain",
    "grand", "grant", "grape", "graph", "grasp", "grass", "grave", "greed",
    "greek", "green", "greet", "grief", "grill", "grind", "grips", "gross",
    "group", "grove", "grown", "guard", "guess", "guest", "guide", "guild",
    "guilt", "habit", "hairs", "hands", "handy", "happy", "hardy", "harms",
    "harsh", "haste", "hasty", "hatch", "haven", "havoc", "hazel", "heads",
    "heals", "heard", "heart", "heavy", "hedge", "heels", "heist", "hello",
    "helps", "herbs", "hints", "hobby", "holds", "holes", "homer", "honey",
    "honor", "hooks", "hopes", "horse", "hosts", "hotel", "hound", "hours",
    "house", "hover", "human", "humid", "humor", "hurry", "icons", "ideal",
    "ideas", "image", "index", "indie", "inner", "input", "intel", "inter",
    "intro", "ionic", "irish", "irony", "issue", "items", "ivory", "jeans",
    "jewel", "joins", "joint", "joker", "jolly", "jones", "judge", "juice",
    "jumbo", "jumps", "kicks", "kinds", "kings", "kites", "knack", "knees",
    "knife", "knock", "knots", "known", "label", "labor", "laced", "lakes",
    "lance", "lands", "lanes", "large", "laser", "lasts", "later", "latex",
    "latin", "laugh", "layer", "leads", "leaks", "leapt", "learn", "lease",
    "least", "leave", "ledge", "legal", "lemon", "level", "lever", "light",
    "liked", "limbs", "limit", "lined", "linen", "liner", "lines", "links",
    "lions", "lists", "lived", "liver", "lives", "loads", "loans", "lobby",
    "local", "locks", "lodge", "lofty", "logic", "logos", "looks", "loops",
    "loose", "lords", "lorry", "loser", "lotus", "loved", "lover", "lower",
    "loyal", "lucky", "lunar", "lunch", "lungs", "lying", "lyric", "macro",
    "magic", "major", "maker", "males", "manor", "maple", "march", "marks",
    "marsh", "masks", "match", "maybe", "mayor", "meals", "means", "media",
    "meets", "melon", "mercy", "merge", "merit", "merry", "messy", "metal",
    "meter", "micro", "might", "miles", "mills", "miner", "minor", "minus",
    "mints", "mixed", "model", "modem", "modes", "moist", "moldy", "money",
    "monks", "month", "moods", "moons", "moral", "motor", "motto", "mount",
    "mouse", "mouth", "moved", "mover", "moves", "movie", "much", "muddy",
    "multi", "mural", "music", "myths", "naive", "named", "names", "nanny",
    "nasty", "naval", "needs", "nerve", "never", "newly", "nexus", "night",
    "ninja", "ninth", "noble", "nodes", "noise", "north", "notch", "noted",
    "notes", "novel", "nurse", "occur", "ocean", "olive", "omega", "onion",
    "opens", "opera", "optic", "orbit", "order", "organ", "other", "ought",
    "outer", "owned", "owner", "oxide", "ozone", "paced", "packs", "pages",
    "pains", "paint", "pairs", "palms", "panel", "panic", "pants", "papal",
    "paper", "parks", "parts", "party", "pasta", "paste", "patch", "paths",
    "patio", "pause", "peace", "peaks", "pearl", "pedal", "penny", "perks",
    "pesos", "petty", "phase", "phone", "photo", "piano", "picks", "piece",
    "piety", "pilot", "pinch", "pines", "pipes", "pitch", "pixel", "pizza",
    "place", "plain", "plane", "plans", "plant", "plate", "plays", "plaza",
    "plead", "plots", "pluck", "plugs", "plumb", "plume", "plump", "plums",
    "plus", "poems", "poets", "point", "poker", "polar", "poles", "polls",
    "ponds", "pools", "porch", "ports", "posed", "poses", "posts", "pouch",
    "pound", "power", "press", "preys", "price", "pride", "prime", "print",
    "prior", "prism", "prize", "probe", "prone", "proof", "props", "prose",
    "proud", "prove", "proxy", "psalm", "pulse", "pumps", "punch", "pupil",
    "puppy", "purse", "queen", "query", "quest", "queue", "quick", "quiet",
    "quilt", "quota", "quote", "radar", "radio", "rails", "rains", "raise",
    "rally", "ranch", "range", "ranks", "rapid", "ratio", "raven", "razor",
    "reach", "reads", "ready", "realm", "rebel", "refer", "reign", "relax",
    "relay", "relic", "remix", "renal", "renew", "repay", "reply", "reset",
    "resin", "retro", "rider", "ridge", "rifle", "right", "rigid", "rings",
    "riots", "risky", "ritzy", "rival", "river", "roads", "roast", "robot",
    "rocks", "rocky", "roger", "roles", "rolls", "roman", "roofs", "rooms",
    "roots", "roses", "rouge", "rough", "round", "route", "royal", "rugby",
    "ruins", "ruled", "ruler", "rules", "rumor", "rural", "rusty", "sadly",
    "safer", "saint", "salad", "sales", "salon", "salsa", "salty", "sands",
    "sandy", "satin", "sauce", "saved", "saves", "scale", "scarf", "scary",
    "scene", "scent", "scope", "score", "scout", "scrap", "seals", "seats",
    "seeds", "seeks", "seems", "seize", "sense", "serve", "setup", "seven",
    "shade", "shaft", "shake", "shall", "shame", "shape", "share", "shark",
    "sharp", "shave", "sheep", "sheer", "sheet", "shelf", "shell", "shift",
    "shine", "shiny", "ships", "shirt", "shock", "shoes", "shoot", "shops",
    "shore", "short", "shots", "shout", "shown", "shows", "sides", "siege",
    "sight", "sigma", "signs", "silly", "since", "sites", "sixth", "sixty",
    "sized", "sizes", "skill", "skins", "skirt", "skull", "slate", "slave",
    "sleek", "sleep", "slice", "slide", "slope", "slump", "small", "smart",
    "smell", "smile", "smoke", "snake", "snaps", "sneak", "snowy", "sober",
    "socks", "solar", "solid", "solve", "songs", "sonic", "sorry", "sorts",
    "souls", "sound", "south", "space", "spare", "spark", "spawn", "speak",
    "spear", "specs", "speed", "spell", "spend", "spent", "spice", "spicy",
    "spike", "spine", "split", "spoke", "spoon", "sport", "spots", "spray",
    "squad", "stack", "staff", "stage", "stain", "stair", "stake", "stamp",
    "stand", "stark", "stars", "start", "state", "stays", "steak", "steal",
    "steam", "steel", "steep", "steer", "stems", "steps", "stick", "stiff",
    "still", "stock", "stomp", "stone", "stood", "stool", "store", "storm",
    "story", "stout", "stove", "strap", "straw", "strip", "stuck", "study",
    "stuff", "style", "sugar", "suite", "sunny", "super", "surge", "swamp",
    "swans", "swear", "sweat", "sweep", "sweet", "swept", "swift", "swing",
    "swiss", "sword", "syrup", "table", "taken", "tales", "talks", "tanks",
    "tapes", "tasks", "taste", "tasty", "taxes", "teach", "teams", "tears",
    "teens", "teeth", "tempo", "tends", "tense", "tenor", "tenth", "terms",
    "tests", "texas", "texts", "thank", "theft", "theme", "thick", "thief",
    "thing", "think", "third", "those", "three", "threw", "throw", "thumb",
    "tiger", "tight", "tiles", "timer", "times", "tints", "tired", "titan",
    "title", "toast", "today", "token", "tombs", "toned", "tones", "tools",
    "tooth", "topic", "torch", "total", "touch", "tough", "tours", "tower",
    "towns", "toxic", "trace", "track", "tract", "trade", "trail", "train",
    "trait", "trash", "treat", "trees", "trend", "trial", "tribe", "trick",
    "tried", "tries", "trims", "trips", "troop", "truck", "truly", "trump",
    "trunk", "trust", "truth", "tulip", "tumor", "tunes", "turbo", "turns",
    "tutor", "tweed", "twice", "twins", "twist", "typed", "types", "uncle",
    "under", "unify", "union", "unite", "units", "unity", "until", "upper",
    "urban", "urged", "usage", "users", "using", "usual", "valid", "value",
    "valve", "vault", "vegas", "venom", "venue", "venus", "verbs", "verse",
    "video", "views", "vinyl", "viola", "viral", "virus", "visit", "vista",
    "vital", "vivid", "vocal", "vodka", "voice", "volts", "voted", "voter",
    "votes", "wages", "wagon", "waist", "walks", "walls", "waltz", "wants",
    "waste", "watch", "water", "watts", "waves", "wears", "weary", "weeds",
    "weeks", "weird", "wells", "welsh", "whale", "wheat", "wheel", "where",
    "which", "while", "white", "whole", "whose", "widen", "wider", "width",
    "winds", "wines", "wings", "wiped", "wires", "witch", "wives", "woman",
    "women", "woods", "words", "works", "world", "worms", "worry", "worse",
    "worst", "worth", "would", "wound", "woven", "wrath", "wreck", "wrist",
    "write", "wrong", "wrote", "yacht", "yards", "years", "yeast", "yield",
    "young", "yours", "youth", "zebra", "zeros", "zesty", "zones"
]


class AgeEncryptionExtension(GObject.GObject, Nautilus.MenuProvider):
    """Main Nautilus extension for age encryption"""

    def __init__(self) -> None:
        super().__init__()
        self._dependencies_checked: bool = False
        self._age_available: Optional[bool] = None
        # Cache for mat2 availability check
        self._mat2_checked: bool = False
        self._mat2_available: Optional[bool] = None
        # Rate limiting: track failed decryption attempts per file
        self._failed_attempts: Dict[str, List[float]] = defaultdict(list)

    def validate_path(self, path: str) -> bool:
        """Validate that a path is safe (no traversal attacks).

        Args:
            path: The path to validate

        Returns:
            True if the path is safe, False otherwise
        """
        # Must be absolute path
        if not os.path.isabs(path):
            logger.warning(f"Path validation failed: not absolute: {path}")
            return False

        # Resolve the path to catch symlink attacks
        try:
            resolved = os.path.realpath(path)
        except (OSError, ValueError) as e:
            logger.warning(f"Path validation failed: cannot resolve: {e}")
            return False

        # Check for path traversal (.. components after resolution)
        # A resolved path should not contain '..'
        if '..' in resolved.split(os.sep):
            logger.warning(f"Path validation failed: traversal detected: {path}")
            return False

        # Don't allow operations on critical system directories
        dangerous_prefixes = ['/bin', '/sbin', '/usr', '/etc', '/var', '/boot', '/root']
        for prefix in dangerous_prefixes:
            if resolved.startswith(prefix + os.sep) or resolved == prefix:
                logger.warning(f"Path validation failed: system directory: {resolved}")
                return False

        return True

    def check_rate_limit(self, file_path: str) -> bool:
        """Check if decryption is rate limited for this file.

        Args:
            file_path: Path to the file being decrypted

        Returns:
            True if allowed to proceed, False if rate limited
        """
        now = time.time()
        attempts = self._failed_attempts[file_path]

        # Clean old attempts (outside the window)
        attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS]
        self._failed_attempts[file_path] = attempts

        if len(attempts) >= RATE_LIMIT_MAX_ATTEMPTS:
            last_attempt = attempts[-1]
            wait_time = RATE_LIMIT_LOCKOUT_SECONDS - (now - last_attempt)
            if wait_time > 0:
                self.show_error("Rate Limited",
                    f"Too many failed attempts.\nWait {int(wait_time)} seconds.")
                return False
        return True

    def record_failed_attempt(self, file_path: str) -> None:
        """Record a failed decryption attempt for rate limiting."""
        self._failed_attempts[file_path].append(time.time())

    def clear_failed_attempts(self, file_path: str) -> None:
        """Clear failed attempts after successful decryption."""
        self._failed_attempts.pop(file_path, None)

    def check_dependencies(self) -> bool:
        """Verify that age is installed (lazy check)"""
        if self._dependencies_checked:
            return self._age_available

        self._dependencies_checked = True
        try:
            subprocess.run(['age', '--version'],
                         capture_output=True,
                         check=True,
                         timeout=2)
            self._age_available = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self._age_available = False

        return self._age_available

    def check_mat2_installed(self) -> bool:
        """Check if mat2 (metadata anonymisation toolkit) is available (lazy check with cache).

        Returns:
            True if mat2 is available, False otherwise
        """
        if self._mat2_checked:
            return self._mat2_available

        self._mat2_checked = True
        try:
            subprocess.run(
                ['mat2', '--version'],
                capture_output=True,
                check=True,
                timeout=2
            )
            self._mat2_available = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self._mat2_available = False

        return self._mat2_available

    def get_file_items(self, *args) -> List:
        """Entry point for context menu items"""
        # If Nautilus was not imported correctly, don't show menu
        if NAUTILUS_VERSION is None:
            return []

        # Verify dependencies (lazy check)
        if not self.check_dependencies():
            # Only show error once per session
            if not hasattr(self, '_error_shown'):
                self._error_shown = True
                self.show_error("age is not installed",
                              "Install age to use this extension:\n\n"
                              "sudo apt install age")
            return []

        # Compatibility between Nautilus 3 and 4
        if len(args) == 1:  # Nautilus 4
            files = args[0]
        else:  # Nautilus 3
            files = args[1]

        if not files:
            return []
        
        # Convert URIs to paths
        paths = []
        for file_info in files:
            if hasattr(file_info, 'get_uri'):
                uri = file_info.get_uri()
                path = self.get_path_from_uri(uri)
                if path:
                    paths.append(path)

        if not paths:
            return []
        
        items = []

        # Detect if all files are .age
        all_age_files = all(p.endswith('.age') for p in paths)

        if all_age_files:
            # Menu for decryption
            items.append(self.create_decrypt_menu_item(paths))
        else:
            # Menu for encryption (handles both files and folders)
            items.append(self.create_encrypt_menu_item(paths))

        return items
    
    def create_encrypt_menu_item(self, paths: List[str]) -> 'Nautilus.MenuItem':
        """Create menu item for encryption (files and/or folders)"""
        # Count files and folders
        num_files = sum(1 for p in paths if os.path.isfile(p))
        num_folders = sum(1 for p in paths if os.path.isdir(p))

        if len(paths) == 1:
            if num_folders == 1:
                label = "Encrypt folder with age"
            else:
                label = "Encrypt with age"
        else:
            parts = []
            if num_files > 0:
                parts.append(f"{num_files} file{'s' if num_files > 1 else ''}")
            if num_folders > 0:
                parts.append(f"{num_folders} folder{'s' if num_folders > 1 else ''}")
            label = f"Encrypt {' + '.join(parts)} with age"

        item = Nautilus.MenuItem(
            name='AgeExtension::EncryptItems',
            label=label,
            tip='Encrypt with age (ChaCha20-Poly1305)'
        )
        item.connect('activate', lambda menu, p=list(paths): self.on_encrypt_items(menu, p))
        return item

    def create_decrypt_menu_item(self, paths: List[str]) -> 'Nautilus.MenuItem':
        """Create menu item for decryption"""
        if len(paths) == 1:
            label = "Decrypt with age"
        else:
            label = f"Decrypt {len(paths)} files with age"

        item = Nautilus.MenuItem(
            name='AgeExtension::DecryptFiles',
            label=label,
            tip='Decrypt .age file(s)'
        )
        item.connect('activate', lambda menu, p=list(paths): self.on_decrypt_files(menu, p))
        return item

    def get_path_from_uri(self, uri: str) -> str:
        """Convert URI to system path"""
        try:
            parsed = urlparse(uri)
            path = unquote(parsed.path)
            return path
        except (ValueError, TypeError) as e:
            logger.warning(f"URI parsing error: {e}")
            return None
    
    def on_encrypt_items(self, menu: 'Nautilus.MenuItem', paths: List[str]) -> None:
        """Handler for encrypting files and/or folders"""
        # Minimal delay to let context menu close
        GLib.timeout_add(50, self._do_encrypt_items, paths)

    def _do_encrypt_items(self, paths: List[str]) -> bool:
        """Encrypt files and folders into a single archive."""
        temp_dir = None
        tar_path = None

        try:
            # 1. Ask for passphrase
            password, _, delete_originals = self.ask_password_method()
            if not password:
                return False

            # Immediate feedback to user
            self.show_notification("Encrypting...", f"⏳ Processing {len(paths)} item(s)")

            clean_metadata = self.check_mat2_installed()

            # 2. Create temp directory
            temp_dir = tempfile.mkdtemp(prefix='age_bundle_')

            # 3. Copy all items to temp
            for item_path in paths:
                item_path = os.path.normpath(item_path)
                basename = os.path.basename(item_path)
                dest = os.path.join(temp_dir, basename)

                if os.path.isfile(item_path):
                    shutil.copy2(item_path, dest)
                elif os.path.isdir(item_path):
                    # Security: Don't follow symlinks to prevent symlink attacks
                    shutil.copytree(item_path, dest, symlinks=False, ignore_dangling_symlinks=True)

            # 4. Clean metadata from all files in temp
            cleaned_count = 0
            if clean_metadata:
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        fp = os.path.join(root, filename)
                        try:
                            result = subprocess.run(
                                ['mat2', '--inplace', '--unknown-members', 'omit', fp],
                                capture_output=True, timeout=60
                            )
                            if result.returncode in (0, 1):
                                cleaned_count += 1
                        except (subprocess.TimeoutExpired, OSError):
                            pass

            # 5. Determine output name and location
            output_dir = os.path.dirname(os.path.normpath(paths[0]))
            if len(paths) == 1:
                bundle_name = os.path.basename(os.path.normpath(paths[0]))
            else:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                bundle_name = f"encrypted_bundle_{timestamp}"

            tar_path = os.path.join(output_dir, f"{bundle_name}.tar.gz")

            # 6. Create tar.gz
            subprocess.run([
                'tar', '-czf', tar_path, '-C', temp_dir, '.'
            ], check=True, capture_output=True)

            # 7. Encrypt
            encrypted_path = f"{tar_path}.age"
            success = self.encrypt_file(tar_path, encrypted_path, password)

            # 8. Cleanup tar (keep only .age) - use try/except to avoid TOCTOU race
            try:
                os.remove(tar_path)
                tar_path = None
            except FileNotFoundError:
                tar_path = None  # Already gone, OK

            # 9. Delete originals if requested
            if success and delete_originals:
                for item_path in paths:
                    item_path = os.path.normpath(item_path)
                    if os.path.isfile(item_path):
                        self.secure_delete(item_path)
                    elif os.path.isdir(item_path):
                        if self.validate_path(item_path):
                            shutil.rmtree(item_path)

            # 10. Notify
            if success:
                msg = f"✅ {len(paths)} item(s) → {os.path.basename(encrypted_path)}"
                if clean_metadata and cleaned_count > 0:
                    msg += f" ({cleaned_count} cleaned)"
                if delete_originals:
                    msg += " (originals deleted)"
                self.show_notification("Done", msg)
            else:
                self.show_error("Error", "Encryption failed")

            return False

        except Exception as e:
            logger.error(f"Encryption error: {e}")
            self.show_error("Error", str(e))
            return False

        finally:
            # Cleanup - use try/except to avoid TOCTOU race conditions
            if tar_path:
                try:
                    os.remove(tar_path)
                except (FileNotFoundError, OSError):
                    pass  # Already gone or inaccessible
            if temp_dir:
                try:
                    shutil.rmtree(temp_dir)
                except (FileNotFoundError, OSError):
                    pass  # Already gone or inaccessible

    def on_decrypt_files(self, menu: 'Nautilus.MenuItem', paths: List[str]) -> None:
        """Handler for decrypting files"""
        GLib.timeout_add(50, self._do_decrypt_files, paths)

    def _do_decrypt_files(self, paths: List[str]) -> bool:
        """Actual decryption logic with rate limiting protection.

        Args:
            paths: List of file paths to decrypt

        Returns:
            False to prevent GLib.timeout_add from repeating
        """
        # Check rate limit for all files before proceeding
        for file_path in paths:
            if not self.check_rate_limit(file_path):
                return False

        # Verify files first
        invalid_files: List[str] = []
        for file_path in paths:
            if not self.verify_age_file(file_path):
                invalid_files.append(os.path.basename(file_path))

        if invalid_files:
            self.show_error("Invalid files",
                          "Not valid .age files:\n" + "\n".join(invalid_files))
            return False

        # Ask for password
        password = self.ask_password("🔓 Decrypt", "Enter password:")
        if not password:
            return False

        success_count: int = 0
        fail_count: int = 0

        for file_path in paths:
            decrypted_path = file_path[:-4] if file_path.endswith('.age') else f"{file_path}.decrypted"

            if self.decrypt_file(file_path, decrypted_path, password):
                success_count += 1
                # Clear rate limit on successful decryption
                self.clear_failed_attempts(file_path)

                # If it's a tar.gz, extract automatically with security validation
                if decrypted_path.endswith('.tar.gz'):
                    try:
                        # Security: Validate tar contents before extraction (zip-slip protection)
                        list_result = subprocess.run(
                            ['tar', '-tzf', decrypted_path],
                            capture_output=True, text=True, timeout=60
                        )
                        if list_result.returncode == 0:
                            for member in list_result.stdout.splitlines():
                                if member.startswith('/') or '..' in member:
                                    raise ValueError(f"Suspicious path in archive: {member}")

                        subprocess.run([
                            'tar', '-xzf', decrypted_path,
                            '-C', os.path.dirname(decrypted_path)
                        ], check=True, capture_output=True)
                        os.remove(decrypted_path)
                    except subprocess.CalledProcessError as e:
                        self.show_error("Error", f"Extraction failed: {e}")
            else:
                fail_count += 1
                # Record failed attempt for rate limiting
                self.record_failed_attempt(file_path)

        if success_count > 0:
            self.show_notification("Done", f"✅ {success_count} file(s) decrypted")

        if fail_count > 0:
            self.show_error("Error", f"Failed: {fail_count} file(s). Check password.")

        return False  # Don't repeat GLib.timeout_add

    def encrypt_file(self, input_path: str, output_path: str, password: str) -> bool:
        """Encrypt a file with age securely using PTY"""
        import time
        master_fd = None
        slave_fd = None
        process = None
        try:
            # age requires a TTY to read passwords interactively
            # We use pty to simulate a terminal
            master_fd, slave_fd = pty.openpty()

            process = subprocess.Popen(
                ['age', '-p', '-o', output_path, input_path],
                stdin=slave_fd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Close slave in parent process
            os.close(slave_fd)
            slave_fd = None

            # Small pause for age to be ready to receive input
            time.sleep(0.1)

            # age -p asks for password twice (entry + confirmation)
            # Security note: password is written directly to PTY fd, never logged
            os.write(master_fd, f"{password}\n".encode('utf-8'))
            time.sleep(0.1)
            os.write(master_fd, f"{password}\n".encode('utf-8'))

            # 120s timeout - age encryption is fast, longer waits indicate problems
            stdout, stderr = process.communicate(timeout=120)

            if process.returncode == 0 and os.path.exists(output_path):
                return True
            else:
                err_msg = stderr.decode('utf-8', errors='replace')
                logger.error(f"Age encryption failed (code {process.returncode}): {err_msg}")
                # Clean up partial output file if exists
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                return False

        except subprocess.TimeoutExpired:
            logger.error("Encryption timeout")
            if process:
                process.kill()
                process.wait()  # Prevent zombie process
            return False
        except OSError as e:
            logger.error(f"Encryption OS error: {e}")
            return False
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return False
        finally:
            # Clean up file descriptors
            if master_fd is not None:
                try:
                    os.close(master_fd)
                except OSError:
                    pass
            if slave_fd is not None:
                try:
                    os.close(slave_fd)
                except OSError:
                    pass

    def decrypt_file(self, input_path: str, output_path: str, password: str) -> bool:
        """Decrypt a .age file securely using PTY"""
        import time
        master_fd = None
        slave_fd = None
        process = None
        try:
            # age requires a TTY to read passwords interactively
            # We use pty to simulate a terminal
            master_fd, slave_fd = pty.openpty()

            process = subprocess.Popen(
                ['age', '-d', '-o', output_path, input_path],
                stdin=slave_fd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Close slave in parent process
            os.close(slave_fd)
            slave_fd = None

            # Small pause for age to be ready to receive input
            time.sleep(0.1)

            # age -d asks for password once
            # Security note: password is written directly to PTY fd, never logged
            os.write(master_fd, f"{password}\n".encode('utf-8'))

            # 120s timeout - age decryption is fast, longer waits indicate problems
            stdout, stderr = process.communicate(timeout=120)

            if process.returncode == 0 and os.path.exists(output_path):
                return True
            else:
                err_msg = stderr.decode('utf-8', errors='replace')
                logger.error(f"Age decryption failed (code {process.returncode}): {err_msg}")
                # Delete failed output file
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                return False

        except subprocess.TimeoutExpired:
            logger.error("Decryption timeout")
            if process:
                process.kill()
                process.wait()  # Prevent zombie process
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            return False
        except OSError as e:
            logger.error(f"Decryption OS error: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            return False
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            return False
        finally:
            # Clean up file descriptors
            if master_fd is not None:
                try:
                    os.close(master_fd)
                except OSError:
                    pass
            if slave_fd is not None:
                try:
                    os.close(slave_fd)
                except OSError:
                    pass

    def verify_age_file(self, file_path: str) -> bool:
        """Verify if a file is a valid .age file"""
        try:
            # Read age file header
            with open(file_path, 'rb') as f:
                header = f.read(100)
                # age files start with "age-encryption.org/v1"
                return b'age-encryption.org/v1' in header
        except (OSError, IOError) as e:
            logger.warning(f"File verification error: {e}")
            return False

    def secure_delete(self, file_path: str) -> None:
        """Delete a file securely using shred"""
        try:
            # -v: verbose, -f: force, -z: add final zero pass, -u: REMOVE file after
            # -n 3: 3 passes (sufficient for SSDs, 10 is excessive)
            subprocess.run(
                ['shred', '-vfzu', '-n', '3', file_path],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Secure delete error: {e}")
            # Fallback to normal rm if shred fails
            try:
                os.remove(file_path)
            except OSError as rm_error:
                logger.error(f"Fallback delete also failed: {rm_error}")

    def clean_metadata(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Clean metadata from a file using mat2, preserving original.

        Creates a temporary copy with cleaned metadata.
        Caller is responsible for deleting the temp file after use.

        Args:
            file_path: Path to the original file (will NOT be modified)

        Returns:
            Tuple of (cleaned_temp_path, error_message)
            - (path, None) if successful - path to cleaned temp file
            - (None, "error") if failed
        """
        if not self.validate_path(file_path):
            return (None, "Invalid file path")

        if not os.path.isfile(file_path):
            return (None, "Not a file")

        temp_path = None
        try:
            # Create temp file with same extension to preserve format
            _, ext = os.path.splitext(file_path)
            fd, temp_path = tempfile.mkstemp(suffix=ext, prefix='age_clean_')
            os.close(fd)

            # Copy original to temp (preserves content but not necessarily all metadata)
            shutil.copy2(file_path, temp_path)

            # Clean metadata on temp copy only
            result = subprocess.run(
                ['mat2', '--inplace', '--unknown-members', 'omit', temp_path],
                capture_output=True,
                timeout=60,
                text=True
            )

            # mat2 return codes:
            # 0 = success (metadata cleaned)
            # 1 = file format not supported (keep copy as-is, still use it)
            if result.returncode in (0, 1):
                logger.info(f"Metadata cleaned: {file_path} -> {temp_path}")
                return (temp_path, None)
            else:
                # Cleanup on error
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                err_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.warning(f"mat2 failed on {file_path}: {err_msg}")
                return (None, err_msg)

        except subprocess.TimeoutExpired:
            logger.error(f"mat2 timeout on: {file_path}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return (None, "Timeout cleaning metadata")

        except FileNotFoundError:
            logger.error("mat2 not found")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return (None, "mat2 not installed")

        except OSError as e:
            logger.error(f"mat2 error on {file_path}: {e}")
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return (None, str(e))

    def ask_password(self, title: str, text: str) -> str:
        """Ask for a password using zenity"""
        try:
            result = subprocess.run(
                ['zenity', '--password',
                 '--title', title,
                 '--text', text],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return None

    def generate_passphrase(self, num_words: int = 24) -> str:
        """Generate a secure passphrase using cryptographically secure random selection.

        Args:
            num_words: Number of words in the passphrase (default: 24)

        Returns:
            A passphrase like "tiger-ocean-mountain-castle-brave-..."
        """
        words = [secrets.choice(PASSPHRASE_WORDLIST) for _ in range(num_words)]
        return '-'.join(words)

    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to system clipboard (Wayland optimized).

        Uses wl-copy directly for Wayland.

        Returns:
            True if clipboard copy succeeded, False otherwise
        """
        try:
            process = subprocess.Popen(
                ['wl-copy'],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.communicate(input=text.encode('utf-8'), timeout=1)
            return process.returncode == 0
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return False

    def ask_password_method(self) -> Tuple[Optional[str], bool, bool]:
        """Generate secure passphrase for encryption.

        No manual password option - always generates secure passphrase
        for maximum security.

        Returns:
            Tuple of (passphrase, confirmed, delete_original)
            - passphrase: The generated passphrase or None if cancelled
            - confirmed: True if user clicked Encrypt or Encrypt & Delete
            - delete_original: True if user clicked Encrypt & Delete
        """
        # Generate passphrase automatically
        passphrase = self.generate_passphrase()

        # Show zenity dialog FIRST (non-blocking start) for faster perceived response
        # Clipboard copy happens in parallel while dialog renders
        try:
            zenity_process = subprocess.Popen(
                ['zenity', '--question',
                 '--title', '🔐 Secure Passphrase',
                 '--text', '📋 Passphrase copied to clipboard!\n\n'
                          f'<tt><b>{passphrase}</b></tt>\n\n'
                          '⚠️ Save this passphrase now!',
                 '--ok-label', '🔒 Encrypt (keep original)',
                 '--cancel-label', 'Cancel',
                 '--extra-button', '🔒🗑️ Encrypt & Delete original',
                 '--width', '550'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Copy to clipboard IN PARALLEL while zenity dialog is rendering
            self.copy_to_clipboard(passphrase)

            # Wait for user response
            stdout, _ = zenity_process.communicate(timeout=300)
            returncode = zenity_process.returncode

            # Check which button was pressed
            if returncode == 0:
                # OK button (Encrypt without delete)
                return (passphrase, True, False)
            elif 'Delete' in stdout:
                # Extra button (Encrypt & Delete)
                return (passphrase, True, True)
            else:
                # Cancel
                return (None, False, False)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            if 'zenity_process' in locals():
                zenity_process.kill()
            return (None, False, False)

    def ask_yes_no(self, title: str, text: str) -> bool:
        """Ask yes/no question using zenity"""
        try:
            result = subprocess.run(
                ['zenity', '--question',
                 '--title', title,
                 '--text', text,
                 '--width', '350'],
                timeout=300
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification (non-blocking)"""
        try:
            subprocess.Popen(
                ['notify-send', '-i', 'dialog-information',
                 title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (FileNotFoundError, OSError):
            pass

    def show_error(self, title: str, message: str) -> None:
        """Show an error dialog"""
        try:
            subprocess.run(
                ['zenity', '--error',
                 '--title', title,
                 '--text', message,
                 '--width', '400'],
                timeout=60
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Fallback to logger if zenity is not available
            logger.error(f"Dialog error: {title} - {message}")
