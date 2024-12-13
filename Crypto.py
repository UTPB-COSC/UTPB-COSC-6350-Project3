
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

keys = {
    0b00: 0xd7ffe8f10f124c56918a614acfc65814,
    0b01: 0x5526736ddd6c4a0592ed33cbc5b1b76d,
    0b10: 0x88863eef1a37427ea0b867227f09a7c1,
    0b11: 0x45355f125db4449eb07415e8df5e27d4
}

def decompose_byte(byte):
    crumbs = []
    for i in range(4):
        crumb = (byte >> (i * 2)) & 0b11
        crumbs.append(crumb)
    return crumbs

def aes_encrypt(data, key):
    key_bytes = key.to_bytes(16, 'big')
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext



# Function to decrypt the AES ciphertext
def aes_decrypt(ciphertext, key):
    try:
        key_bytes = key.to_bytes(16, 'big')
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        
        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        
        return unpadded_data.decode()
    except Exception:
        return None


def decompose_byte(byte):
    crumbs = []
    crumb = byte & 0b11
    crumbs.append(crumb)
    byte = byte >> 2
    crumb = byte & 0b11
    crumbs.append(crumb)
    byte = byte >> 2
    crumb = byte & 0b11
    crumbs.append(crumb)
    byte = byte >> 2
    crumb = byte & 0b11
    crumbs.append(crumb)
    return crumbs


def recompose_byte(crumbs):
    return crumbs[3] >> 6 + crumbs[2] >> 4 + crumbs[1] >> 2 + crumbs[0]
