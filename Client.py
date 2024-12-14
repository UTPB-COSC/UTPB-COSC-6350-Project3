# Imported packages
import socket
import struct
import random
import sys
import os
from Crypto import keys, aes_decrypt, recompose_byte
import time

# File directory
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Crypto.data')

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

def recv_all(client_socket, size):
    """
    Helper function to ensure all bytes are received.
    """
    data = b''
    while len(data) < size:
        packet = client_socket.recv(size - len(data))
        if not packet:
            raise ConnectionError("Connection closed while receiving data.")
        data += packet
    return data

#Start timer for program
start_time = time.time()

def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Step 1: Connect to the server
        print(f"[INFO] Initiating connection to the server...")
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[INFO] Connected to {SERVER_HOST}:{SERVER_PORT}")

        #Step 2: Receive PAYLOAD
        payload_size_data = recv_all(client_socket, 4)  # Receive 4 bytes for payload size
        payload_size = struct.unpack('!I', payload_size_data)[0]  # Unpack size
        print(f"[DEBUG] Received payload size: {payload_size}")
        PAYLOAD = recv_all(client_socket, payload_size).decode('utf-8')  # Receive and decode PAYLOAD
        print(f"[INFO] Expected PAYLOAD: {PAYLOAD}")

        # Step 3: Receive total crumbs (first 4 bytes)
        data = recv_all(client_socket, 4)  # Use recv_all for safety
        total_crumbs = struct.unpack('!I', data)[0]
        print(f"[INFO] Total crumbs to receive: {total_crumbs}")

        crumbs = [None] * total_crumbs
        attempted_keys = [[] for _ in range(total_crumbs)]
        num_decoded = 0
        completion = 0
        ref_payload_size = 0

        while num_decoded < total_crumbs:
            for i in range(total_crumbs):
                encrypted_payload = client_socket.recv(1024)
                if crumbs[i] is None:

                    possible_crumbs = [0b00, 0b01, 0b10, 0b11]
                    crumb = random.choice(possible_crumbs)
                    key = keys[crumb]
                    while key in attempted_keys[i]:
                        crumb = random.choice(possible_crumbs)
                        key = keys[crumb]
                    attempted_keys[i].append(key)

                    try:
                        # Decrypt the payload
                        decrypted_payload = aes_decrypt(encrypted_payload, key)
                        if decrypted_payload == PAYLOAD:
                            #print(f"[DEBUG] Successfully decrypted crumb {i} with key: {key.hex()}")
                            crumbs[i] = crumb # Store the crumb ID
                            num_decoded += 1
                    except:
                        pass

                completion = (num_decoded / total_crumbs) * 100
                #print(f"Sending ACK for {completion}% to server...")
                client_socket.sendall(bytes(f"{completion:.2f}", encoding="UTF-8"))#struct.pack('!f', completion))
            print(f"Current completion: {completion:.2f}%")

        #if completion == 1.0:
        decoded_bytes = bytes(recompose_byte(crumbs[i:i + 4]) for i in range(0, len(crumbs), 4))
        print("[INFO] File successfully received and decoded.")

        with open(file_path, 'wb') as f: # TODO
            f.write(decoded_bytes)

if __name__ == "__main__":
    tcp_client()
