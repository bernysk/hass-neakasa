"""AES-CBC helpers for the Neakasa web API login token."""

from __future__ import annotations

import time
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .const import AES_IV_DEFAULT, AES_KEY_DEFAULT


class APIEncryption:
    """Encrypts request tokens with the keys handed out at login."""

    def __init__(self) -> None:
        """Start with the app's default key and IV."""
        self.reset()

    def reset(self) -> None:
        """Forget the login token and fall back to the default key and IV."""
        self.aes_key = AES_KEY_DEFAULT
        self.aes_iv = AES_IV_DEFAULT
        self._token = ""

    def _pad(self, data: bytes) -> bytes:
        """Zero-pad to the 16-byte AES block size, as the Neakasa app does."""
        pad_len = (-len(data)) % 16
        return data + (b"\x00" * pad_len)

    def _unpad(self, data: bytes) -> bytes:
        """Strip the zero padding (also drops genuine trailing NUL bytes)."""
        return data.rstrip(b"\x00")

    def encrypt(self, plain_text: str) -> str:
        """Encrypt *plain_text* and return it base64-encoded."""
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_iv))
        encryptor = cipher.encryptor()
        padded = self._pad(plain_text.encode("utf-8"))
        ct = encryptor.update(padded) + encryptor.finalize()
        return b64encode(ct).decode("utf-8")

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt base64 *encrypted_text*, tolerating '+' sent as spaces."""
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_iv))
        decryptor = cipher.decryptor()
        raw = b64decode(encrypted_text.replace(" ", "+"))
        pt_padded = decryptor.update(raw) + decryptor.finalize()
        return self._unpad(pt_padded).decode("utf-8")

    def _get_timestamp(self) -> str:
        return format(time.time(), ".6f")

    def get_token(self) -> str:
        """Return a fresh, timestamped request token."""
        return self.encrypt(self._token + "@" + self._get_timestamp())

    def decode_login_token(self, login_token: str) -> None:
        """Extract the token, user ID and per-session key/IV from *login_token*."""
        self.reset()

        parts = self.decrypt(login_token).split("@")

        if len(parts) >= 1:
            self._token = parts[0]
        if len(parts) >= 2:
            self.userid = parts[1]
            self.uid = self.encrypt(parts[1])
        if len(parts) >= 3:
            self.aes_key = parts[2].encode()
        if len(parts) >= 4:
            self.aes_iv = parts[3].encode()
