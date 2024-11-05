import socket
from Crypto import *
import random

# Constants
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Function to connect to the server and receive packets
def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"[INFO] Connected to {SERVER_HOST}:{SERVER_PORT}")

            # Continuously receive encrypted packets
            while True:
                encrypted_packet = client_socket.recv(1024)
                if not encrypted_packet:
                    break

                # Attempt to decrypt using one of the keys
                for key in keys.values():
                    try:
                        decrypted_message = aes_decrypt(encrypted_packet, key)
                        if "The quick brown fox jumps over the lazy dog." in decrypted_message:
                            print(f"[INFO] Successfully decrypted: {decrypted_message}")
                            client_socket.sendall(b'ACK')
                            break
                    except Exception:
                        continue
                else:
                    print(f"[WARN] Failed to decrypt packet.")
                    client_socket.sendall(b'NACK')

        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
        finally:
            print(f"[INFO] Connection closed.")

if __name__ == "__main__":
    tcp_client()
