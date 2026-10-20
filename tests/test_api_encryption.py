"""Tests for APIEncryption."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.neakasa.api_encryption import APIEncryption


def test_encrypt_decrypt_roundtrip() -> None:
    enc = APIEncryption()
    token = enc.encrypt("hello-world")
    assert token
    assert enc.decrypt(token) == "hello-world"


def test_pad_full_block() -> None:
    enc = APIEncryption()
    assert enc._pad(b"x" * 16) == b"x" * 16


def test_pad_partial_block() -> None:
    enc = APIEncryption()
    padded = enc._pad(b"abc")
    assert padded == b"abc" + (b"\x00" * 13)
    assert len(padded) % 16 == 0


def test_unpad() -> None:
    enc = APIEncryption()
    assert enc._unpad(b"abc\x00\x00") == b"abc"


def test_decrypt_accepts_spaces_instead_of_plus() -> None:
    enc = APIEncryption()
    token = enc.encrypt("spaces")
    spaced = token.replace("+", " ")
    assert enc.decrypt(spaced) == "spaces"


def test_get_timestamp() -> None:
    enc = APIEncryption()
    with patch(
        "custom_components.neakasa.api_encryption.time.time",
        return_value=1730000000.123456,
    ):
        assert enc._get_timestamp() == "1730000000.123456"


def test_get_token() -> None:
    enc = APIEncryption()
    enc._token = "tok123"
    token = enc.get_token()
    decrypted = enc.decrypt(token)
    assert decrypted.startswith("tok123@")


def test_decode_login_token_single_part() -> None:
    enc = APIEncryption()
    token = enc.encrypt("onlytoken")
    enc.decode_login_token(token)
    assert enc._token == "onlytoken"


def test_decode_login_token_two_parts() -> None:
    enc = APIEncryption()
    token = enc.encrypt("mytoken@userid1")
    enc.decode_login_token(token)
    assert enc._token == "mytoken"
    assert enc.userid == "userid1"
    assert enc.uid == enc.encrypt("userid1")


def test_decode_login_token_full() -> None:
    enc = APIEncryption()
    token = enc.encrypt("mytoken@userid1@newkey16byte!!@newiv16bytes!!")
    enc.decode_login_token(token)
    assert enc._token == "mytoken"
    assert enc.userid == "userid1"
    assert enc.aes_key == b"newkey16byte!!"
    assert enc.aes_iv == b"newiv16bytes!!"
