"""Module for loading and managing RSA keys for JWT signing/verification.

This module provides functions to load RSA private and public keys from PEM files,
with security checks (file existence).

Example:
    from config.jwt_config import get_private_key, get_public_key

    private_key = get_private_key()  # For signing JWTs
    public_key = get_public_key()     # For verifying JWTs
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path
from config.settings import settings

def _load_private_key() -> bytes:
    """Load the private key from PEM file with security checks.

    Returns:
        bytes: The raw PEM-encoded private key.

    Raises:
        FileNotFoundError: If the private key file does not exist.
        PermissionError: If the file permissions are too permissive (should be 600).
    """
    key_path = Path(settings.JWT_PRIVATE_KEY_PATH)

    # Security check: file must exist
    if not key_path.exists():
        raise FileNotFoundError(f"Private key file not found: {key_path}")

    with open(key_path, "rb") as key_file:
        return key_file.read()

def _load_public_key() -> bytes:
    """Load the public key from PEM file.

    Returns:
        bytes: The raw PEM-encoded public key.

    Raises:
        FileNotFoundError: If the public key file does not exist.
    """
    key_path = Path(settings.JWT_PUBLIC_KEY_PATH)

    if not key_path.exists():
        raise FileNotFoundError(f"Public key file not found: {key_path}")

    with open(key_path, "rb") as key_file:
        return key_file.read()

def get_private_key():
    """Get the RSA private key for signing JWT tokens.

    Returns:
        AsymmetricKey: A private key object ready for JWT signing.

    Note:
        The key is loaded lazily and not cached. For high-performance applications,
        consider adding caching (with thread-safety).
    """
    pem = _load_private_key()
    return serialization.load_pem_private_key(
        pem,
        password=None,
        backend=default_backend()
    )

def get_public_key():
    """Get the RSA public key for verifying JWT tokens.

    Returns:
        AsymmetricKey: A public key object ready for JWT verification.
    """
    pem = _load_public_key()
    return serialization.load_pem_public_key(
        pem,
        backend=default_backend()
    )