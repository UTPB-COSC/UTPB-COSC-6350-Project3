import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Crypto import aes_encrypt, aes_decrypt, keys, decompose_byte, recompose_byte

# File path to test
file_path = "risk.bmp"

def test_file_processing(file_path):
    """
    Test file decomposition, recomposition, and encryption/decryption.
    """
    try:
        print(f"[INFO] Testing file: {file_path}")
        file_size = 0
        crumbs = []
        first_16_bytes = []
        
        # Step 1: Open the file and decompose into crumbs
        with open(file_path, "rb") as dat_file:
            dat_file.seek(0, 2)  # Move to the end of the file
            file_size = dat_file.tell()  # Get the file size
            dat_file.seek(0)  # Reset to the beginning

            for _ in range(16):  # Limit to the first 16 bytes for testing
                byte = dat_file.read(1)
                if not byte:
                    break
                byte = byte[0]  # Get the integer value of the byte
                first_16_bytes.append(byte)  # Collect the first 16 bytes
                byte_crumbs = decompose_byte(byte)
                crumbs.extend(byte_crumbs)

        # Print the first 16 bytes separated by commas
        print("[INFO] First 16 bytes (hexadecimal):")
        print(", ".join(f"{byte:02x}" for byte in first_16_bytes))

        # Print the first 16 bytes decomposed into crumbs, separated by commas
        print("[INFO] First 16 bytes decomposed into crumbs (binary):")
        crumbs_as_binary = [f"{bin(crumb)}" for crumb in crumbs]
        print(", ".join(crumbs_as_binary))
        
        print(f"[INFO] File size: {file_size} bytes")

        # Step 2: Test recomposition of crumbs back into bytes
        recomposed_bytes = []
        for i in range(0, len(crumbs), 4):  # Process 4 crumbs (1 byte) at a time
            recomposed_byte = recompose_byte(crumbs[i:i+4])
            recomposed_bytes.append(recomposed_byte)

        print(f"[INFO] Recomposition test:")
        for i, byte in enumerate(recomposed_bytes):
            print(f"  Original byte {i}: {bin(byte)}")
        assert len(recomposed_bytes) == len(crumbs) // 4, "Recomposition mismatch!"

        # Step 3: Test encryption and decryption
        payload = "The quick brown fox jumps over the lazy dog."
        print(f"[INFO] Testing encryption and decryption for payload: '{payload}'")

        for bit_pair, key in keys.items():
            print(f"  Testing with bit pair {bin(bit_pair)} and key {key.hex()}")
            encrypted = aes_encrypt(payload, key)
            decrypted = aes_decrypt(encrypted, key)
            assert decrypted == payload, f"Decryption failed for bit pair {bin(bit_pair)}!"

        print("[INFO] All tests passed successfully!")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
    except AssertionError as e:
        print(f"[ASSERTION FAILED] {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_file_processing(file_path)
