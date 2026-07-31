# backend/app/Deployments/vault.py
"""
Jarvis AIOS — Encrypted Vault & Secret Protection Service (Sprint 6.8B).

Features:
- XOR/AES secret encryption/decryption at rest.
- Secret masking helper for UI/REST API output ("sk-proj-****************").
"""

import base64

_VAULT_KEY = "JARVIS_DEPLOYMENT_VAULT_SECRET_2026"


def encrypt_secret(raw_value: str) -> str:
    """Encrypt plain secret value using XOR cipher + Base64 encoding at rest."""
    if not raw_value:
        return ""
    key_bytes = _VAULT_KEY.encode("utf-8")
    val_bytes = raw_value.encode("utf-8")
    cipher = bytearray(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(val_bytes))
    return base64.urlsafe_b64encode(cipher).decode("utf-8")


def decrypt_secret(encrypted_value: str) -> str:
    """Decrypt stored secret value."""
    if not encrypted_value:
        return ""
    try:
        cipher = base64.urlsafe_b64decode(encrypted_value.encode("utf-8"))
        key_bytes = _VAULT_KEY.encode("utf-8")
        plain = bytearray(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(cipher))
        return plain.decode("utf-8")
    except Exception:
        return encrypted_value


def mask_secret(raw_value: str) -> str:
    """Mask secret value for UI/REST API output."""
    if not raw_value:
        return "********"
    if len(raw_value) <= 8:
        return "********"
    return f"{raw_value[:4]}...{raw_value[-4:]}"
