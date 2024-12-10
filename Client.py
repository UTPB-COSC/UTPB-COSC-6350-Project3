import socket
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Crypto import aes_decrypt, keys

# Constants
SERVER_HOST = '127.0.0.1'  # Change this to the server's IP if it's running on a different machine
SERVER_PORT = 5555         # Port number for the TCP connection
EXPECTED_PAYLOAD = "The quick brown fox jumps over the lazy dog."  # Expected decrypted payload
TIMEOUT = 600

BUFFER_SIZE = 1024

def decode_packet(encrypted_payload, key):
    return aes_decrypt(encrypted_payload, key)

def tcp_client():
    try:
        print("[INFO] Connecting to server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(TIMEOUT)
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("[INFO] Connected to server.")

            # Receive total packets count from server
            total_packets = int(client_socket.recv(1024).decode('utf-8'))
            print(f"[INFO] Total packets to receive: {total_packets}")
            client_socket.sendall(b"READY")  # Notify server that client is ready

            packets_received = 0
            last_progress = 0

            while True:
                # Receive encrypted packet from server
                encrypted_packet = client_socket.recv(1024)
                if not encrypted_packet:
                    print("[ERROR] Received an empty packet.")
                    break

                if encrypted_packet == b"END":
                    print(f"[INFO] Transmission complete. Received all {total_packets} packets.")
                    break

                # Attempt decryption with all keys
                decrypted_message = None
                for key in keys.values():
                    try:
                        decrypted_message = aes_decrypt(encrypted_packet, key)
                        if decrypted_message == EXPECTED_PAYLOAD:
                            break
                    except Exception:
                        continue

                if decrypted_message:
                    packets_received += 1
                    # Send acknowledgment back to the server
                    client_socket.sendall(f"ACK:{packets_received - 1}".encode('utf-8'))

                    # Print progress at 10% intervals
                    current_progress = (packets_received / total_packets) * 100
                    if current_progress >= last_progress + 10:
                        last_progress += 10
                        print(f"[INFO] Client transmission progress: {last_progress}% completed.")
                        print(f"[INFO] Decrypted message: {decrypted_message}")
                else:
                    # If decryption fails, send a NACK
                    client_socket.sendall(b"NACK")

    except Exception as e:
        print(f"[ERROR] Client encountered an error: {e}")
    finally:
        print("[INFO] Connection closed.")

if __name__ == "__main__":
    tcp_client()
