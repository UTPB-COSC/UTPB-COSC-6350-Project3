from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Define four AES keys to be used for encryption and decryption (in bytes)
keys = {
    0b00: bytes.fromhex('d7ffe8f10f124c56918a614acfc65814'),  # 16 bytes (128 bits)
    0b01: bytes.fromhex('5526736ddd6c4a0592ed33cbc5b1b76d'),  # 16 bytes (128 bits)
    0b10: bytes.fromhex('88863eef1a37427ea0b867227f09a7c1'),  # 16 bytes (128 bits)
    0b11: bytes.fromhex('45355f125db4449eb07415e8df5e27d4')  # 16 bytes (128 bits)
}

# Function to encrypt a string using AES
def aes_encrypt(plaintext, key):
    iv = os.urandom(16)  # Generate a random 16-byte IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the plaintext to be AES block size (16 bytes) compatible
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()

    # Encrypt the padded plaintext
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Return the IV concatenated with the ciphertext (to be used in decryption)
    return iv + ciphertext

# Function to decrypt the AES ciphertext
def aes_decrypt(ciphertext, key):
    # Extract the IV from the first 16 bytes
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]

    # Create cipher object using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()

    # Unpad the plaintext to retrieve the original data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(padded_plaintext) + unpadder.finalize()

    # Return the original plaintext as a string
    return unpadded_data.decode()

# Function to decompose a byte into 4 crumbs (2 bits each)
def decompose_byte(byte):
    crumbs = []
    for _ in range(4):
        crumb = byte & 0b11  # Extract the last 2 bits
        crumbs.append(crumb)
        byte >>= 2  # Shift the byte right by 2 bits
    return crumbs

# Function to recompose a byte from 4 crumbs
def recompose_byte(crumbs):
    return (crumbs[3] << 6) + (crumbs[2] << 4) + (crumbs[1] << 2) + crumbs[0]
