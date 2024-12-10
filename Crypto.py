from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Predefined AES keys for 4 polarizations (converted to bytes)
# Each key corresponds to a unique 2-bit value (00, 01, 10, 11)
keys = {
    0b00: bytes.fromhex("d7ffe8f10f124c56918a614acfc65814"), # Key for horizontal polarization (00)
    0b01: bytes.fromhex("5526736ddd6c4a0592ed33cbc5b1b76d"), # Key for vertical polarization (01)
    0b10: bytes.fromhex("88863eef1a37427ea0b867227f09a7c1"), # Key for clockwise polarization (10)
    0b11: bytes.fromhex("45355f125db4449eb07415e8df5e27d4") # Key for counterclockwise polarization (11)
}

# Function to encrypt a string using AES
def aes_encrypt(plaintext, key):
    iv = os.urandom(16) # Generate a random 16-byte IV

    # Create cipher object using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor() # Create encryptor

    # Pad the plaintext to be AES block size (16 bytes) compatible
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    # Encrypt the padded data
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Return the IV concatenated with the ciphertext (to be used in decryption)
    return iv + ciphertext

# Function to decrypt the AES ciphertext
def aes_decrypt(ciphertext, key):
    # Extract the IV from the first 16 bytes
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]

    # Create cipher object using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    # Create decryptor
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # Return the original plaintext as a string
    return unpadded_data.decode()

def decompose_byte(byte):
    crumbs = [(byte >> (i * 2)) & 0b11 for i in range(4)] # Extract each 2-bit crumb
    return crumbs[::-1] # Reverse the order to match the desired representation

def recompose_byte(crumbs):
    byte = 0 # Initialize the byte to 0
    for i, crumb in enumerate(crumbs[::-1]): # Process crumbs in reverse order
        byte |= (crumb & 0b11) << (i * 2) # Shift and combine the crumbs into the byte
    return byte
