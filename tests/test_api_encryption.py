"""Tests for APIEncryption."""

from __future__ import annotations

from unittest.mock import patch

from custom_components.neakasa.api_encryption import APIEncryption


async def test_encrypt_decrypt_roundtrip() -> None:
    enc = APIEncryption()
    token = await enc.encrypt("hello-world")
    assert token
    assert await enc.decrypt(token) == "hello-world"


async def test_pad_full_block() -> None:
    enc = APIEncryption()
    assert await enc._pad(b"x" * 16) == b"x" * 16


async def test_pad_partial_block() -> None:
    enc = APIEncryption()
    padded = await enc._pad(b"abc")
    assert padded == b"abc" + (b"\x00" * 13)
    assert len(padded) % 16 == 0


async def test_unpad() -> None:
    enc = APIEncryption()
    assert await enc._unpad(b"abc\x00\x00") == b"abc"


async def test_decrypt_accepts_spaces_instead_of_plus() -> None:
    enc = APIEncryption()
    token = await enc.encrypt("spaces")
    spaced = token.replace("+", " ")
    assert await enc.decrypt(spaced) == "spaces"


async def test_get_timestamp() -> None:
    enc = APIEncryption()
    with patch(
        "custom_components.neakasa.api_encryption.time.time",
        return_value=1730000000.123456,
    ):
        assert await enc._get_timestamp() == "1730000000.123456"


async def test_get_token() -> None:
    enc = APIEncryption()
    enc._token = "tok123"
    token = await enc.getToken()
    decrypted = await enc.decrypt(token)
    assert decrypted.startswith("tok123@")


async def test_decode_login_token_single_part() -> None:
    enc = APIEncryption()
    token = await enc.encrypt("onlytoken")
    await enc.decodeLoginToken(token)
    assert enc._token == "onlytoken"


async def test_decode_login_token_two_parts() -> None:
    enc = APIEncryption()
    token = await enc.encrypt("mytoken@userid1")
    await enc.decodeLoginToken(token)
    assert enc._token == "mytoken"
    assert enc.userid == "userid1"
    assert enc.uid == await enc.encrypt("userid1")


async def test_decode_login_token_full() -> None:
    enc = APIEncryption()
    token = await enc.encrypt("mytoken@userid1@newkey16byte!!@newiv16bytes!!")
    await enc.decodeLoginToken(token)
    assert enc._token == "mytoken"
    assert enc.userid == "userid1"
    assert enc.aes_key == b"newkey16byte!!"
    assert enc.aes_iv == b"newiv16bytes!!"
