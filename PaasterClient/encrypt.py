import os
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from hashlib import md5


def bytes_to_key(data: bytes, salt: bytes, output=48) -> bytes:
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key

    return final_key[:output]


def encrypt_for_cryptojs(plain: bytes, passphrase: str) -> bytes:
    """Encrypt a plaintext string with a passphrase suitable for crypto-js.

    Parameters
    ----------
    plain : bytes
    passphrase : str

    Returns
    -------
    bytes
        Encrypted bytes
    """

    salt = os.urandom(8)

    key_iv = bytes_to_key(
        passphrase.encode(),
        salt
    )
    key = key_iv[:32]
    iv = key_iv[32:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain)
    padded_data += padder.finalize()

    return base64.b64encode(
        b"Salted__" + salt + encryptor.update(padded_data)
    )
