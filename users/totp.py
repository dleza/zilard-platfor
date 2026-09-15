import base64
import hmac
import hashlib
import struct
import time


def _normalise_secret(secret: str) -> bytes:
    padding = "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode((secret + padding).upper())


def generate_totp(secret: str, timestep: int | None = None, interval: int = 30) -> str:
    counter = int((time.time() if timestep is None else timestep) // interval)
    key = _normalise_secret(secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code % 1_000_000:06d}"


def verify_totp(secret: str, code: str, window: int = 1, interval: int = 30) -> bool:
    if not secret or not code or not code.isdigit():
        return False
    now = int(time.time())
    for drift in range(-window, window + 1):
        if hmac.compare_digest(generate_totp(secret, now + (drift * interval), interval), code):
            return True
    return False

def generate_secret() -> str:
    """Generate a random base32 TOTP secret (same scheme User.save() uses)."""
    import base64
    import os

    return base64.b32encode(os.urandom(20)).decode("utf-8").rstrip("=")


def provisioning_uri(secret: str, account_name: str, issuer: str = "DLDMS") -> str:
    """Build an otpauth:// URI an authenticator app's QR scanner understands."""
    from urllib.parse import quote

    label = quote(f"{issuer}:{account_name}")
    return (
        f"otpauth://totp/{label}"
        f"?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"
    )
