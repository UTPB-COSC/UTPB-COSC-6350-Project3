import socket
import threading
import struct
from Crypto.Cipher import AES
from Crypto import keys  

HOST = '127.0.0.1'
PORT = 5555

def get_crumbs(file_bytes, num_crumbs=4):
    # Divide file into equal parts
    crumb_size = len(file_bytes) // num_crumbs
    crumbs = [file_bytes[i * crumb_size: (i + 1) * crumb_size] for i in range(num_crumbs - 1)]
    crumbs.append(file_bytes[(num_crumbs - 1) * crumb_size:])  # Last chunk gets remaining bytes
    return crumbs

def encrypt_with_key(plaintext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    block_size = 16
    pad_len = block_size - (len(plaintext) % block_size)
    padded = plaintext + bytes([pad_len])*pad_len
    return cipher.encrypt(padded)

def handle_client(conn, addr, crumbs):
    # Send total number of crumbs
    total_crumbs = len(crumbs)
    conn.sendall(struct.pack('!I', total_crumbs))
    print(f"[SERVER] Sent total crumb count: {total_crumbs}")

    while True:
        print("[SERVER] Starting a new transmission pass of all crumbs...")
        for i, crumb in enumerate(crumbs):
            key = keys[f'{i:02b}']  # Use key '00', '01', '10', '11' for crumbs
            ciphertext = encrypt_with_key(crumb, key)
            length = len(ciphertext)

            print(f"[SERVER] Sending crumb {i+1}/{total_crumbs} with key '{i:02b}'")
            conn.sendall(struct.pack('!I', length))
            conn.sendall(ciphertext)

        print("[SERVER] All crumbs for this pass sent. Waiting for client fraction...")
        data = conn.recv(8)
        if not data:
            print("[SERVER] No fraction received, assuming client disconnected.")
            break

        fraction = struct.unpack('!d', data)[0]
        print(f"[SERVER] Received fraction from client: {fraction}")

        if fraction >= 1.0:
            print("[SERVER] Client has fully decoded the file. Ending connection.")
            break

    conn.close()
    print("[SERVER] Connection closed.")

def main():
    with open('textFile.txt', 'rb') as f:
        file_bytes = f.read()

    crumbs = get_crumbs(file_bytes)  # Split file into 4 crumbs
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print("[SERVER] Listening on", (HOST, PORT))

    while True:
        conn, addr = s.accept()
        print("[SERVER] Connection from", addr)
        t = threading.Thread(target=handle_client, args=(conn, addr, crumbs))
        t.start()

if __name__ == '__main__':
    main()
