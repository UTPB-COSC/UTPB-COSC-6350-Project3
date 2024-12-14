from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import time

keys = {
    0b00: b'\xd7\xff\xe8\xf1\x0f\x12\x4c\x56\x91\x8a\x61\x4a\xcf\xc6\x58\x14',
    0b01: b'\x55\x26\x73\x6d\xdd\x6c\x4a\x05\x92\xed\x33\xcb\xc5\xb1\xb7\x6d',
    0b10: b'\x88\x86\x3e\xef\x1a\x37\x42\x7e\xa0\xb8\x67\x22\x7f\x09\xa7\xc1',
    0b11: b'\x45\x35\x5f\x12\x5d\xb4\x44\x9e\xb0\x74\x15\xe8\xdf\x5e\x27\xd4'
}

PAYLOAD = "The quick brown fox jumps over the lazy dog."

def aes_decrypt(ciphertext, key):
    iv = ciphertext[:16]
    actual_ciphertext = ciphertext[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data.decode()

def recompose_byte(crumbs):
    return sum(crumb << (i * 2) for i, crumb in enumerate(crumbs))


import socket
import struct
import random

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555


def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"[CLIENT] Connected to {SERVER_HOST}:{SERVER_PORT}")

            total_crumbs = struct.unpack('!I', client_socket.recv(4))[0]
            print(f"[CLIENT] Total crumbs to receive: {total_crumbs}")
            crumbs = [None] * total_crumbs
            attempted_keys = [[] for _ in range(total_crumbs)]
            num_decoded = 0
            completion = 0
            ref_payload_size = 0
            print(
                f"[CLIENT] Receiving crumbs from server."
            )
            while num_decoded < total_crumbs:
                for i in range(total_crumbs):
                    if crumbs[i] is not None:
                        continue

                    payload_size = struct.unpack('!I', client_socket.recv(4))[0]
                    ref_payload_size = payload_size
                    encrypted_payload = client_socket.recv(payload_size)
                    available_keys = [key for key in keys.values() if key not in attempted_keys[i]]

                    if not available_keys:
                        continue

                    key = random.choice(available_keys)

                    try:
                        decrypted_payload = aes_decrypt(encrypted_payload, key)
                        if decrypted_payload == PAYLOAD:
                            crumb = next(k for k, v in keys.items() if v == key)
                            crumbs[i] = crumb
                            num_decoded += 1
                            new_completion = num_decoded / total_crumbs
                            if round(new_completion, 2) != round(completion, 2):
                                print(f"[CLIENT] Decoding progress: {completion:.0%}")
                            completion = new_completion
                        else:
                            attempted_keys[i].append(key)
                    except:
                        pass

                print(f"[CLIENT] Sending ACK for {completion:.0%} to server...")
                client_socket.sendall(struct.pack('!f', completion))

            if completion >= 1.0:
                decoded_bytes = bytes(recompose_byte(crumbs[i:i + 4]) for i in range(0, len(crumbs), 4))
                client_socket.sendall(struct.pack('!f', completion))
                print("[CLIENT] File successfully received and decoded.")
            else:
                print("[CLIENT] File not completely received from server.")

            # flush extra data crumbs
            while (extra_recv := client_socket.recv(4)) == struct.pack('!I', ref_payload_size):
                client_socket.recv(ref_payload_size)

            if extra_recv[:3] != b'ACK':
                print("[CLIENT] Did not receive proper acknowledgment from server")

        except Exception as e:
            print(f"[CLIENT] An error occurred: {e}")
        finally:
            print(f"[CLIENT] Connection closed.")


if __name__ == "__main__":
    tcp_client()
