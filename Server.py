import socket
from concurrent.futures import ThreadPoolExecutor
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Crypto import aes_encrypt, keys, decompose_byte

# Constants
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5555       # Port number
TIMEOUT = 600     # 10 minutes (in seconds)
MAX_THREADS = 10  # Maximum number of threads in the pool
MAX_INVALID_PACKETS = 10  # Maximum invalid packets before stopping
EXPECTED_PAYLOAD = "The quick brown fox jumps over the lazy dog."

file_path = os.path.join(os.path.dirname(__file__), "risk.bmp")

def encode_payload(payload, bit_pair):
    if bit_pair not in keys:
        print(f"[WARN] Missing key for bit pair value: {bit_pair}")
        return None
    key = keys[bit_pair]
    return aes_encrypt(payload, key)

# Function to handle client connection
def handle_client(conn, addr):
    conn.settimeout(TIMEOUT)
    print(f"[INFO] Connection established with {addr}.")

    try:
        with open(file_path, "rb") as file:
            crumbs = []
            byte = file.read(1)
            while byte:
                byte_value = byte[0]
                crumbs.extend(decompose_byte(byte_value))
                byte = file.read(1)

        total_packets = len(crumbs)
        print(f"[INFO] Sending {total_packets} packets to client {addr}.")

        # Send the total number of packets to the client
        conn.sendall(str(total_packets).encode())
        client_ack = conn.recv(1024).decode('utf-8')

        if client_ack != "READY":
            print(f"[ERROR] Client {addr} not ready. Closing connection.")
            return

        packets_sent = 0
        last_progress = 0

        # Send packets with progress tracking 
        for i, crumb in enumerate(crumbs):
            try:
                bit_pair_value = crumb
                if bit_pair_value not in keys:
                    print(f"[WARN] Missing key for bit pair value: {bit_pair_value}. Skipping packet {i}.")
                    continue

                key = keys[bit_pair_value]
                encrypted_packet = encode_payload(EXPECTED_PAYLOAD, bit_pair_value)

                ack_received = False
                while not ack_received:
                    conn.sendall(encrypted_packet)
                    try:
                        ack = conn.recv(1024).decode('utf-8')
                        if ack == f"ACK:{i}":
                            packets_sent += 1
                            current_progress = (packets_sent / total_packets) * 100

                            # Print progress at 10%
                            if current_progress >= last_progress + 10:
                                last_progress += 10
                                print(f"[INFO] Server progress: {last_progress}% completed ({packets_sent}/{total_packets} packets)")

                            ack_received = True
                        else:
                            print(f"[WARN] Unexpected response from client: {ack}. Resending packet {i}...")
                    except socket.timeout:
                        print(f"[WARN] Timeout waiting for ACK for packet {i}. Resending...")
            except KeyError as e:
                print(f"[ERROR] Key error for bit pair value {bit_pair_value}: {e}. Skipping packet {i}.")
                continue

        conn.sendall(b"END")
        print(f"[INFO] Server progress: 100% completed ({total_packets}/{total_packets} packets).")

    except Exception as e:
        print(f"[ERROR] Error handling client {addr}: {e}")

    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception:
            pass
        print(f"[INFO] Connection from {addr} has been closed.")

def start_server():
    print(f"[INFO] Server starting on {HOST}:{PORT}")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as pool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"[INFO] Server is listening on port {PORT}...")
            while True:
                conn, addr = server_socket.accept()
                pool.submit(handle_client, conn, addr)

if __name__ == "__main__":
    start_server()
