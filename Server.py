import socket
from concurrent.futures import ThreadPoolExecutor
import struct
from Crypto import keys, aes_encrypt, decompose_byte, aes_decrypt,recompose_byte

HOST = '127.0.0.1'
PORT = 5555
TIMEOUT = 600
MAX_THREADS = 10

PAYLOAD = "The quick brown fox jumps over the lazy dog."

def handle_client(conn, addr):
    conn.settimeout(TIMEOUT)
    print(f"[INFO] Connection from {addr} established.")

    # Send PAYLOAD
    payload_size = len(PAYLOAD)
    conn.sendall(struct.pack('!I', payload_size))  # Send size of PAYLOAD
    conn.sendall(PAYLOAD.encode('utf-8'))  # Send PAYLOAD
    print(f"[DEBUG - TESTING] Sent PAYLOAD size: {payload_size}")  # TESTING
    print(f"[DEBUG - TESTING] Sent PAYLOAD: {PAYLOAD}")  # TESTING

    with open("README.md", "rb") as file:
        file_content = file.read()

    crumbs = []
    for byte in file_content:
        crumbs.extend(decompose_byte(byte))

    total_crumbs = len(crumbs)
    print(f"[INFO] Total crumbs: {total_crumbs}")
    conn.sendall(struct.pack('!I', total_crumbs))
    print(f"[DEBUG - TESTING] Sent total crumbs count: {total_crumbs}")  # TESTING

    print(f"[DEBUG] Entering crumbs sending loop...")  # Debugging log
    while True:
        completion = 0
        print(f"Sending crumbs to client...")
        for i, crumb in enumerate(crumbs):

            key = keys[crumb]
            encrypted_payload = aes_encrypt(PAYLOAD, key)

            completion = float(conn.recv(1024))

        print(f"Current completion: {completion:.2f}%")
        if completion >= 100.0:
            print("[INFO] File fully transmitted and decoded by client.")
            # Acknowledge receipt of completion status
            #conn.sendall(b'ACK')
            conn.close()
            print(f"[DEBUG - TESTING] Sent ACK to client.")  # TESTING
            break


def start_server():
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"[INFO] Server started, listening on {PORT}...")
            while True:
                conn, addr = server_socket.accept()
                print(f"[INFO] Accepted connection from {addr}.")
                executor.submit(handle_client, conn, addr)

#Code for testing/debugging -  Either run "python Server.py" to start server or "python Server.py test" to run test.
def test_encryption_decryption():
    # Example test payload
    test_payload = "The quick brown fox jumps over the lazy dog."
    test_key = bytes.fromhex('d7ffe8f10f124c56918a614acfc65814')  # Use one of your existing keys

    try:
        # Encrypt the payload
        encrypted_payload = aes_encrypt(test_payload, test_key)
        print(f"[INFO] Encrypted payload (hex): {encrypted_payload.hex()}")

        # Decrypt the payload
        decrypted_payload = aes_decrypt(encrypted_payload, test_key)
        print(f"[INFO] Decrypted payload: {decrypted_payload}")

        # Validate decryption
        assert decrypted_payload == test_payload, "[ERROR] Decryption did not match original payload!"
        print("[INFO] Encryption and decryption test passed successfully.")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

def test_byte_reassembly():
    # Example byte to test
    test_byte = 0xAB  # Arbitrary test byte (binary: 10101011)

    try:
        # Decompose the byte
        crumbs = decompose_byte(test_byte)
        print(f"[INFO] Decomposed crumbs: {crumbs}")

        # Reassemble the byte
        reassembled_byte = recompose_byte(crumbs)
        print(f"[INFO] Reassembled byte: {hex(reassembled_byte)}")

        # Validate reassembly
        assert test_byte == reassembled_byte, "[ERROR] Byte reassembly test failed!"
        print("[INFO] Byte reassembly test passed successfully.")
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")


if __name__ == "__main__":
   # start_server()
   import sys
   if len(sys.argv) > 1 and sys.argv[1] == "test":
       # Run tests only
       print("[INFO] Running tests...")
       test_encryption_decryption()
       test_byte_reassembly()
   else:
       # Start the server
       print("[INFO] Starting the server...")
       start_server()
