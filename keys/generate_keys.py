"""
RSA Key Generation Module for JWT Authentication

This module generates a new pair of RSA private/public keys for JWT signing and verification.
The keys are saved in PEM format (PKCS#8 for private key, SubjectPublicKeyInfo for public key)
and stored in the `keys/keys/` directory.

Security Notes:
    - The private key is saved WITHOUT password encryption by default (for development).
    - In production, use `encryption_algorithm=serialization.BestAvailableEncryption(b'password')`.
    - The generated keys use RSA-2048 with public exponent 65537 (standard for JWT).

Usage:
    # Generate keys (development)
    python -m keys.generate_keys
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# --- Private Key Generation ---
# Generates a new RSA key pair using OpenSSL backend.
# public_exponent=65537: Standard value for RSA (balances speed and security).
# key_size=2048: Minimum recommended size for JWT (4096 for high-security environments).
# backend=default_backend(): Uses OpenSSL as the cryptographic backend.
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# --- Private Key Serialization & Storage ---
# Serializes the private key to PKCS#8 PEM format:
# - Encoding.PEM: Base64-encoded text format with headers.
# - PrivateFormat.PKCS8: Standard format for private keys (RFC 5208).
# - NoEncryption(): Key is stored in plaintext (for development only).
#   For production, use BestAvailableEncryption(b'password') to encrypt the key.
with open('keys/keys/jwt_private_key.pem', 'wb') as f:
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
        # encryption_algorithm=serialization.BestAvailableEncryption(b'password')
    )
    f.write(pem)

# --- Public Key Extraction & Storage ---
# Extracts the public key from the private key object.
# The public key is a mathematical derivation of the private key and cannot be reversed.
# Serializes to SubjectPublicKeyInfo PEM format (most widely compatible).
public_key = private_key.public_key()
with open('keys/keys/jwt_public_key.pem', 'wb') as f:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    f.write(pem)

# --- Completion Feedback ---
# Prints a success message to confirm key generation.
print('✅ RSA keys have been generated in keys/keys/')
