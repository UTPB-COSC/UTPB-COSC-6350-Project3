import socket
from concurrent.futures import ThreadPoolExecutor

HOST = '0.0.0.0'  # Server host
PORT = 5555       # Server port
TIMEOUT = 600     # Connection timeout in seconds
MAX_THREADS = 10  # Maximum number of threads in the thread pool

# Placeholder for encryption keys and AES encryption function
keys = {0: "key0", 1: "key1", 2: "key2", 3: "key3"}


def aes_encrypt(message, key):
    # Placeholder for actual AES encryption logic
    return message.encode()


# Function to handle client connection
def handle_client(conn, addr):
    conn.settimeout(TIMEOUT)
    print(f"[INFO] Connection from {addr[0]}:{addr[1]} established.")
    try:
        # Load message from risk.bmp file and decompose into crumbs (simulated packets)
        with open("risk.bmp", "rb") as dat_file:
            dat_file.seek(0, 2)  # Move to the end of the file to get its size
            file_size = dat_file.tell()
            dat_file.seek(0)  # Reset to the beginning of the file
            crumbs = [int.from_bytes(dat_file.read(1), 'big') % 4 for _ in range(file_size)]

        total_packets = len(crumbs)
        print(f"[INFO] Total packets to send: {total_packets}")

        # Calculate progress intervals for every 10%
        progress_intervals = [int(total_packets * i / 10) for i in range(1, 11)]

        # Start sending packets to the client
        for i, crumb in enumerate(crumbs):
            key = keys[crumb]
            encrypted_packet = aes_encrypt("The quick brown fox jumps over the lazy dog.", key)
            conn.sendall(encrypted_packet)

            # Print progress at every 10%
            if (i + 1) in progress_intervals:
                progress = ((i + 1) / total_packets) * 100
                print(f"[INFO] Progress: {progress:.1f}% completed ({i + 1}/{total_packets} packets)")

        # Send end of transmission message
        conn.sendall(b'END')
        print(f"[INFO] Transmission complete to {addr[0]}")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception as e:
            print(f"[ERROR] Error closing connection from {addr}: {e}")
        print(f"[INFO] Connection from {addr[0]}:{addr[1]} closed.")


# Main server function
def start_server():
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:  # Fixed max_threads to max_workers
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print("[INFO] Server started")
            print(f"[INFO] Listening on {HOST}:{PORT}")
            print("[INFO] Waiting for connections...")

            while True:
                conn, addr = server_socket.accept()
                print(f"[INFO] Accepted connection from {addr}")
                executor.submit(handle_client, conn, addr)


if __name__ == "__main__":
    start_server()
