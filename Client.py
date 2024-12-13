import socket
import struct
import random
from Crypto import *

HOST = '127.0.0.1'  # Local host
PORT = 5555         # Same port as server
STANDARD_MESSAGE = "quantum secured transmission"

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            print("Attempting to connect to server...")
            client_socket.connect((HOST, PORT))
            print("Connected to server!")
            
            # Get total number of crumbs from server
            crumb_count = struct.unpack('!I', client_socket.recv(4))[0]
            print(f"Expecting {crumb_count} crumbs")
            
            if crumb_count == 0:
                print("Server reported error with file")
                return
            
            # Tell server we're ready
            client_socket.sendall("READY".encode())
            
            # Initialize storage for decoded crumbs
            decoded_crumbs = {}
            attempted_keys = {}
            
            while len(decoded_crumbs) < crumb_count:
                # Receive index and encrypted data
                index = struct.unpack('!I', client_socket.recv(4))[0]
                data_len = struct.unpack('!I', client_socket.recv(4))[0]
                encrypted_data = client_socket.recv(data_len)
                
                # Track which keys we've tried for this crumb
                if index not in attempted_keys:
                    attempted_keys[index] = set()
                
                # Try to decrypt with each unused key
                for crumb_value, key in keys.items():
                    if key not in attempted_keys[index]:
                        attempted_keys[index].add(key)
                        try:
                            decrypted = aes_decrypt(encrypted_data, key)
                            if decrypted == STANDARD_MESSAGE:
                                decoded_crumbs[index] = crumb_value
                                break
                        except Exception:
                            continue
                
                # Calculate and send completion percentage
                completion = (len(decoded_crumbs) / crumb_count) * 100
                client_socket.sendall(f"{completion}".encode())
                
                print(f"Progress: {completion:.1f}%")
                
                # Check for potential eavesdropping
                if len(attempted_keys) > 10:  # After trying several crumbs
                    expected = len(attempted_keys) * 0.25  # Should decode ~25% of attempts
                    if len(decoded_crumbs) < expected * 0.5:  # Less than half expected
                        print("WARNING: Possible eavesdropping detected!")
            
            # Reconstruct file from crumbs
            print("Reconstructing file...")
            bytes_data = bytearray()
            for i in range(0, crumb_count, 4):
                byte = 0
                for j in range(4):
                    if i + j < crumb_count:
                        byte |= (decoded_crumbs[i + j] & 0b11) << (j * 2)
                bytes_data.append(byte)
            
            # Save reconstructed file
            with open("received_risk.bmp", "wb") as file:
                file.write(bytes_data)
            print("File saved as 'received_risk.bmp'")
            
        except ConnectionRefusedError:
            print("Could not connect to server. Is it running?")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Connection closed")

if __name__ == "__main__":
    start_client()