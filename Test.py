from Crypto import *

# Test the decompose and recompose functions
def test_byte_functions():
    byte = 0b11010111
    crumbs = decompose_byte(byte)
    recomposed = recompose_byte(crumbs)
    assert byte == recomposed, "Decompose and recompose failed!"
    print("[INFO] Decompose and recompose test passed.")

# Test the encryption and decryption functions
def test_crypto_functions():
    plaintext = "The quick brown fox jumps over the lazy dog."
    key = keys[0b00]
    ciphertext = aes_encrypt(plaintext, key)
    decrypted_text = aes_decrypt(ciphertext, key)
    assert plaintext == decrypted_text, "Encryption and decryption failed!"
    print("[INFO] Encryption and decryption test passed.")

if __name__ == "__main__":
    test_byte_functions()
    test_crypto_functions()
