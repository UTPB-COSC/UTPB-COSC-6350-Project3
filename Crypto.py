from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Define four AES keys for different polarizations
keys = {
    0b00: bytes.fromhex('d7ffe8f10f124c56918a614acfc65814'),  # Horizontal
    0b01: bytes.fromhex('5526736ddd6c4a0592ed33cbc5b1b76d'),  # Vertical
    0b10: bytes.fromhex('88863eef1a37427ea0b867227f09a7c1'),  # Clockwise
    0b11: bytes.fromhex('45355f125db4449eb07415e8df5e27d4')  # Counter-clockwise
}


def aes_encrypt(plaintext, key):
    """Encrypt a string using AES-CBC mode"""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext


def aes_decrypt(ciphertext, key):
    """Decrypt AES-CBC ciphertext"""
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data.decode()


def decompose_byte(byte):
    """Split byte into 4 pairs of 2 bits"""
    crumbs = []
    for i in range(4):
        crumb = (byte >> (i * 2)) & 0b11
        crumbs.append(crumb)
    return crumbs


def recompose_byte(crumbs):
    """Combine 4 pairs of 2 bits into a byte"""
    byte = 0
    for i, crumb in enumerate(crumbs):
        byte |= (crumb & 0b11) << (i * 2)
    return byte