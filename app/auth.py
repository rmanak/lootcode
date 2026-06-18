"""Password hashing and credential validation for optional accounts (V2).

Hashing uses the standard library's `hashlib.scrypt` (memory-hard, OpenSSL-backed)
so there's no native dependency to build on a home server. The stored value is a
self-describing string `scrypt$n$r$p$salt_hex$hash_hex`, which lets us tune the
work factor later without breaking existing hashes. See docs/user-accounts-v2.md.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re

# scrypt work factors. n must be a power of two; memory use ~= 128*n*r*p bytes
# (~16 MB here), comfortably runnable on a small LAN box.
_N, _R, _P, _DKLEN = 1 << 14, 8, 1, 32
_MAXMEM = 64 * 1024 * 1024

MIN_PASSWORD_LEN = 8
_USERNAME_RE = re.compile(r"^[a-z0-9._-]{3,32}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_N, r=_R, p=_P,
                        maxmem=_MAXMEM, dklen=_DKLEN)
    return f"scrypt${_N}${_R}${_P}${salt.hex()}${dk.hex()}"


def verify_password(password: str, encoded: str | None) -> bool:
    """Constant-time check of `password` against a stored hash. False on any
    malformed/empty hash (e.g. a guest row that was never claimed)."""
    if not encoded:
        return False
    try:
        scheme, n, r, p, salt_hex, hash_hex = encoded.split("$")
        if scheme != "scrypt":
            return False
        salt, expected = bytes.fromhex(salt_hex), bytes.fromhex(hash_hex)
        dk = hashlib.scrypt(password.encode("utf-8"), salt=salt,
                            n=int(n), r=int(r), p=int(p),
                            maxmem=_MAXMEM, dklen=len(expected))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(dk, expected)


def normalize_username(raw: str) -> str:
    """Lowercase + trim. Usernames are stored lowercased so login and the unique
    index are case-insensitive; the separate display `name` keeps any casing."""
    return (raw or "").strip().lower()


def validate_username(raw: str) -> str:
    """Return the normalized username or raise ValueError with a user-facing message."""
    username = normalize_username(raw)
    if not _USERNAME_RE.match(username):
        raise ValueError(
            "Username must be 3–32 characters: letters, digits, '.', '_' or '-'.")
    return username


def normalize_email(raw: str | None) -> str | None:
    """Lowercase + trim; empty/blank becomes None (email is optional)."""
    email = (raw or "").strip().lower()
    return email or None


def validate_email(raw: str | None) -> str | None:
    """Return a normalized email or None. Raise ValueError if non-empty but invalid."""
    email = normalize_email(raw)
    if email is not None and not _EMAIL_RE.match(email):
        raise ValueError("That doesn't look like a valid email address.")
    return email


def validate_password(password: str) -> str:
    if len(password or "") < MIN_PASSWORD_LEN:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LEN} characters.")
    return password
