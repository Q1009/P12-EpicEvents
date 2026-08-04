"""
Token Management Module for CLI Applications

Handles secure persistence of JWT tokens in a JSON file.
- Stores tokens in ~/.epicevents/tokens.json
- Applies secure file permissions (600)
- Manages token loading/saving/clearing
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone


# Path for tokens' directory (in user's home directory)
CONFIG_DIR = Path.home() / ".epicevents"
TOKEN_FILE = CONFIG_DIR / "tokens.json"


def _ensure_directory() -> None:
    """Create the config directory with secure permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Restrict directory to owner only (700 = rwx------)
    os.chmod(CONFIG_DIR, 0o700)

def save_tokens(access_token: str, refresh_token: str) -> None:
    """
    Save tokens to disk with secure permissions.

    Args:
        access_token: JWT access token
        refresh_token: JWT refresh token
    """
    _ensure_directory()

    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Write to a temporary file first (atomic operation)
    temp_file = TOKEN_FILE.with_suffix(".tmp")
    with open(temp_file, "w") as f:
        json.dump(data, f, indent=2)

    # Atomically replace the old file
    temp_file.replace(TOKEN_FILE)
    # Set file permissions to owner read/write only (600 = rw-------)
    os.chmod(TOKEN_FILE, 0o600)

def load_tokens() -> Optional[Dict[str, Any]]:
    """
    Load tokens from disk if they exist.

    Returns:
        Dictionary with tokens and user info, or None if file doesn't exist or is invalid.
    """
    if not TOKEN_FILE.exists():
        return None

    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)

        # Validate required fields
        required_keys = {"access_token", "refresh_token", "user"}
        if not required_keys.issubset(data.keys()):
            clear_tokens()  # Corrupted file, delete it
            return None

        return data
    except (json.JSONDecodeError, IOError):
        return None

def clear_tokens() -> None:
    """Delete the token file if it exists."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()

def tokens_exist() -> bool:
    """Check if format valid tokens are stored."""
    return TOKEN_FILE.exists() and load_tokens() is not None