import socket
from concurrent.futures import ThreadPoolExecutor
import time
import os
from Crypto import *

# Constants
HOST = '0.0.0.0'
PORT = 5555
TIMEOUT = 600
MAX_THREADS = 10


def handle_client(conn, addr):
    """Handle individual client connections"""
    conn.settimeout(TIMEOUT)
    print(f"\n[INFO] Connection from {addr} established.")
    print("[INFO] Starting transmission...")
    print("[INFO] Test message: 'The quick brown fox jumps over the lazy dog.'")

    try:
        # Read and process input file
        with open("requirements.txt", "rb") as dat_file:
            dat_file.seek(0, 2)
            file_size = dat_file.tell()
            dat_file.seek(0)

            print(f"[INFO] File size: {file_size} bytes")

            # Read file and decompose into crumbs
            crumbs = []
            for _ in range(file_size):
                byte = int.from_bytes(dat_file.read(1), 'big')
                crumbs.extend(decompose_byte(byte))

        # Calculate total packets and send to client
        total_packets = len(crumbs)
        conn.sendall(str(total_packets).encode())
        client_ack = conn.recv(1024)  # Wait for client acknowledgment

        packets_sent = 0
        last_progress_milestone = 0

        print(f"[INFO] Total packets to send: {total_packets}")
        print("\n[INFO] Transmission Progress:")
        print("----------------------------------------")

        # Send packets
        for i, crumb in enumerate(crumbs):
            key = keys[crumb]
            message = "The quick brown fox jumps over the lazy dog."
            encrypted_packet = aes_encrypt(message, key)

            ack_received = False
            while not ack_received:
                conn.sendall(encrypted_packet)

                try:
                    ack = conn.recv(1024)
                    if ack == b'ACK':
                        packets_sent += 1
                        current_progress = (packets_sent / total_packets) * 100

                        # Show progress at 25% intervals
                        if current_progress >= 25 and last_progress_milestone < 25:
                            print(f"\n[INFO] Progress: 25% completed ({packets_sent}/{total_packets} packets)")
                            last_progress_milestone = 25
                        elif current_progress >= 50 and last_progress_milestone < 50:
                            print(f"\n[INFO] Progress: 50% completed ({packets_sent}/{total_packets} packets)")
                            last_progress_milestone = 50
                        elif current_progress >= 75 and last_progress_milestone < 75:
                            print(f"\n[INFO] Progress: 75% completed ({packets_sent}/{total_packets} packets)")
                            last_progress_milestone = 75

                        ack_received = True
                    else:
                        print(f"[WARN] Invalid ACK from {addr} for packet {i}. Resending...")
                        time.sleep(1)
                except socket.timeout:
                    print(f"[WARN] Timeout waiting for ACK from {addr} for packet {i}.")
                    time.sleep(1)

        # Send END signal and show final progress
        conn.sendall(b'END')
        print(f"\n[INFO] Progress: 100% completed ({total_packets}/{total_packets} packets)")
        print("\n[INFO] Transmission complete to {addr}.")
        print("----------------------------------------")

    except Exception as e:
        print(f"[ERROR] Error handling client {addr}: {e}")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception:
            pass
        print(f"[INFO] Connection from {addr} closed.")


def start_server():
    """Start server and accept client connections"""
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"\n[INFO] Server started")
            print(f"[INFO] Listening on {HOST}:{PORT}")
            print("[INFO] Waiting for connections...")

            while True:
                conn, addr = server_socket.accept()
                executor.submit(handle_client, conn, addr)


if __name__ == "__main__":
    start_server()