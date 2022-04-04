# -*- coding: utf-8 -*-

"""
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def password_encrypt(secret: str, raw_data: bytes) -> str:
    """Encrypt raw data with AES - CBC algorithm with secret derivation.

    Parameters
    ----------
    secret : str
    raw_data : bytes

    Returns
    -------
    str
        Encrypted data hex encoded with IV & salt.
    """

    padder = padding.PKCS7(
        algorithms.AES.block_size  # type: ignore
    ).padder()
    padded_data = padder.update(raw_data) + padder.finalize()

    salt = os.urandom(128)
    iv = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=32,
        salt=salt,
        iterations=50000
    )

    cipher = Cipher(
        algorithms.AES(kdf.derive(secret.encode())),
        modes.CBC(iv)
    )
    encryptor = cipher.encryptor()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return (
        iv.hex() + "," + salt.hex() + "," +
        encrypted_data.hex()
    )
