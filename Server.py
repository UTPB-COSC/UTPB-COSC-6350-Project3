import socket
from concurrent.futures import ThreadPoolExecutor
from Crypto import *
import time

# Constants
HOST = '0.0.0.0'
PORT = 5555
TIMEOUT = 600
MAX_THREADS = 10

# Function to handle client connection
def handle_client(conn, addr):
    conn.settimeout(TIMEOUT)
    print(f"[INFO] Connection from {addr} established.")
    try:
        # Load file and decompose into crumbs (bit pairs)
        file_size = 0
        crumbs = []
        with open("risk.bmp", "rb") as dat_file:
            dat_file.seek(0, 2)
            file_size = dat_file.tell()
            dat_file.seek(0)
            for _ in range(file_size):
                byte = dat_file.read(1)[0]
                crumbs += decompose_byte(byte)

        # Start sending packets to the client
        for crumb in crumbs:
            key = keys[crumb]
            message = "The quick brown fox jumps over the lazy dog."
            encrypted_packet = aes_encrypt(message, key)
            conn.sendall(encrypted_packet)

            # Wait for acknowledgment
            ack = conn.recv(1024)
            if ack.decode('utf-8') != 'ACK':
                print(f"[WARN] No ACK received from {addr}. Resending packet...")
                time.sleep(1)  # Delay before resending
                conn.sendall(encrypted_packet)
            else:
                print(f"[INFO] Packet acknowledged by {addr}.")
    except Exception as e:
        print(f"[ERROR] Error handling client {addr}: {e}")
    finally:
        # Close connection
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception as e:
            print(f"[ERROR] Error closing connection from {addr}: {e}")
        print(f"[INFO] Connection from {addr} has been closed.")

# Main server function
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

if __name__ == "__main__":
    start_server()
