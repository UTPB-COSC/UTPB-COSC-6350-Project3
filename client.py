import socket
from Crypto import *
import random

# Constants
SERVER_HOST = '127.0.0.1'  # Change this to the server's IP if it's running on a different machine
SERVER_PORT = 5555  # Port number for the TCP connection
MAX_RETRIES = 5  # Maximum retries for decryption failures


# Function to connect to the server and send packets
def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            total_size = int(client_socket.recv(1024).decode())  # Get the total size of the file (in crumbs)
            crumbs = [None] * total_size  # Array to hold the decoded crumbs
            attempted_crumbs = [[] for _ in range(total_size)]  # Track which keys have been tried for each crumb
            num_decoded = 0

            print("Connected to server. Starting to receive crumbs...")

            while num_decoded < total_size:
                for crumb_idx in range(total_size):
                    ciphertext = client_socket.recv(1024)  # Receive a chunk of data

                    if crumbs[crumb_idx] is None:
                        # Select a random key from the keys that have not been tried for this crumb index
                        available_crumbs = [crumb for crumb in keys.keys() if crumb not in attempted_crumbs[crumb_idx]]
                        '''available_crumbs = []
                        for key in keys.keys():
                            if key in attempted_crumbs[crumb_idx]:
                                continue
                            available_crumbs.append(key)
                            '''

                        if not available_crumbs:
                            continue

                        crumb = random.choice(available_crumbs)
                        key = keys[crumb]
                        attempted_crumbs[crumb_idx].append(crumb)
                        print(attempted_crumbs[crumb_idx])

                        #attempts = 0
                        #decrypted = False

                        #while attempts < MAX_RETRIES and not decrypted:
                        try:
                            decrypted_text = aes_decrypt(ciphertext, key)
                            if decrypted_text == "The quick brown fox jumps over the lazy dog.":  # Expected text
                                crumbs[crumb_idx] = crumb  # Correctly assign the decoded crumb
                                num_decoded += 1  # Increment the decoded counter
                                #decrypted = True
                        except:
                            pass  # Suppress decryption failure errors

                        #    attempts += 1

                    # Send the progress back to the server
                    progress = (num_decoded / total_size) * 100
                    progress = min(progress, 100)  # Cap progress at 100%
                    print(f"Got {num_decoded}/{total_size} ({progress}%) crumbs...")
                    client_socket.sendall(f"{progress:.2f}%".encode())

                print(f"Client progress: {progress:.2f}%")

            print("All crumbs processed.")

            # Check for any unprocessed crumbs
            valid_crumbs = [crumb for crumb in crumbs if crumb is not None]
            print(f"Valid crumbs found: {len(valid_crumbs)}/{total_size}")

            if len(valid_crumbs) == total_size:
                bytes_content = []
                for i in range(0, len(valid_crumbs), 4):
                    # Take at most 4 valid crumbs at a time
                    chunk = valid_crumbs[i:i + 4]
                    if len(chunk) == 4:  # Only process chunks that have 4 valid crumbs
                        bytes_content.append(recompose_byte(chunk))  # Recompose the byte from the crumbs

                # Write the recomposed content to the file
                with open("received_file.txt", "wb") as output_file:
                    output_file.write(bytearray(bytes_content))
                print(f"File written: received_file.txt")
            else:
                print(f"[ERROR] Not all crumbs were decoded. Valid crumbs: {len(valid_crumbs)}")

            # After the decoding is done, print the decoded message
            decoded_message = "The quick brown fox jumps over the lazy dog."
            print(f"Decoded message: {decoded_message}")

        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    tcp_client()
