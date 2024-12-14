from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

keys = {
    0b00: b'\xd7\xff\xe8\xf1\x0f\x12\x4c\x56\x91\x8a\x61\x4a\xcf\xc6\x58\x14',
    0b01: b'\x55\x26\x73\x6d\xdd\x6c\x4a\x05\x92\xed\x33\xcb\xc5\xb1\xb7\x6d',
    0b10: b'\x88\x86\x3e\xef\x1a\x37\x42\x7e\xa0\xb8\x67\x22\x7f\x09\xa7\xc1',
    0b11: b'\x45\x35\x5f\x12\x5d\xb4\x44\x9e\xb0\x74\x15\xe8\xdf\x5e\x27\xd4'
}

PAYLOAD = "The quick brown fox jumps over the lazy dog."

def aes_encrypt(plaintext, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext

def decompose_byte(byte):
    return [(byte >> i) & 0b11 for i in range(0, 8, 2)]

import socket
from concurrent.futures import ThreadPoolExecutor
import struct

HOST = '0.0.0.0'
PORT = 5555
TIMEOUT = 600
MAX_THREADS = 10


def handle_client(conn, addr):
    conn.settimeout(TIMEOUT)
    print(f"[SERVER] Connection from {addr} established.")
    try:
        with open("checker.jpeg", "rb") as file: #A smaller file used for simplicity
            file_content = file.read()

        crumbs = []
        for byte in file_content:
            crumbs.extend(decompose_byte(byte))

        total_crumbs = len(crumbs)
        print(f"[SERVER] Total crumbs: {total_crumbs}")
        conn.sendall(struct.pack('!I', total_crumbs))

        while True:
            for i, crumb in enumerate(crumbs):
                key = keys[crumb]
                encrypted_payload = aes_encrypt(PAYLOAD, key)
                conn.sendall(struct.pack('!I', len(encrypted_payload)))
                conn.sendall(encrypted_payload)

            # After sending all crumbs, get overall completion
            completion_data = conn.recv(4)
            if not completion_data:
                print("[SERVER] Client disconnected.")
                break

            completion = struct.unpack('!f', completion_data)[0]
            print(f"[CLIENT] Decoding Completion = {completion:.2%}")

            if round(completion,4) >= 0.99:
                print("[SERVER] File fully transmitted and decoded by client.")
                # Acknowledge receipt of completion status
                conn.sendall(b'ACK')
                break

    except Exception as e:
        print(f"[SERVER] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[SERVER] Connection from {addr} closed.")


def start_server():
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"[SERVER] Server started, listening on {PORT}...")

            while True:
                conn, addr = server_socket.accept()
                print(f"[SERVER] Accepted connection from {addr}.")
                executor.submit(handle_client, conn, addr)

if __name__ == "__main__":
    start_server()