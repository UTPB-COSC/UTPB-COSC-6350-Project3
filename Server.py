import socket
import struct
from Crypto import *

HOST = '0.0.0.0'  
PORT = 5555
STANDARD_MESSAGE = "quantum secured transmission"

def handle_client(conn, addr):
    try:
        print(f"Client connected from {addr}")
        print("DEBUG: Starting file read...")
        
        # Read and decompose file
        crumbs = []
        try:
            with open("risk.bmp", "rb") as file:
                print("Reading file...")
                # Read file size
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                print(f"DEBUG: File size: {file_size} bytes")
                # Read and decompose file
                data = file.read()
                for byte in data:
                    crumbs.extend(decompose_byte(byte))
                
            print(f"File decomposed into {len(crumbs)} crumbs")
            print("DEBUG: Sending crumb count to client...")
            
            # Send total number of crumbs to client
            conn.sendall(struct.pack('!I', len(crumbs)))
            
            # Wait for client acknowledgment
            ack = conn.recv(1024).decode()
            if ack != "READY":
                raise Exception("Client not ready")
            
            # Send each crumb
            for i, crumb in enumerate(crumbs):
                # Get encryption key for this crumb
                key = keys[crumb]
                
                # Encrypt standard message with this key
                encrypted = aes_encrypt(STANDARD_MESSAGE, key)
                
                # Send index and encrypted data
                conn.sendall(struct.pack('!I', i))  # Send index
                conn.sendall(struct.pack('!I', len(encrypted)))  # Send length
                conn.sendall(encrypted)  # Send encrypted data
                
                # Get completion percentage
                completion = float(conn.recv(1024).decode())
                print(f"Transfer progress: {completion:.1f}%")
                
                if completion >= 100:
                    break
            
            print("File transfer completed")
            
        except FileNotFoundError:
            print("Error: risk.bmp not found")
            conn.sendall(struct.pack('!I', 0))  # Send 0 crumbs to indicate error
            
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection closed with {addr}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server started, listening on port {PORT}...")
        
        try:
            while True:
                conn, addr = server_socket.accept()
                handle_client(conn, addr)
                
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_server()