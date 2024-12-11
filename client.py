import socket
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Placeholder for decryption keys and AES decryption function
keys = {0: "key0", 1: "key1", 2: "key2", 3: "key3"}


def aes_decrypt(encrypted_message, key):
    # Placeholder for actual AES decryption logic
    return encrypted_message.decode()


# Function to connect to the server and receive packets
def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("[INFO] Connected to 127.0.0.1:5555")

            total_packets = 6422616
            successfully_decrypted = 0
            final_unique_message = None

            print(f"[INFO] Expecting {total_packets} packets")

            # Progress intervals
            progress_intervals = [int(total_packets * i / 10) for i in range(1, 11)]

            # Continuously receive encrypted packets
            for current_packet in range(1, total_packets + 1):
                encrypted_packet = client_socket.recv(1024)

                # Attempt decryption with each key
                for key in keys.values():
                    try:
                        decrypted_message = aes_decrypt(encrypted_packet, key)
                        if "The quick brown fox jumps over the lazy dog." in decrypted_message:
                            # Store only the exact message once
                            if final_unique_message is None:
                                final_unique_message = "The quick brown fox jumps over the lazy dog."
                                successfully_decrypted += 1
                            break
                    except Exception:
                        continue

                # Update and print progress at every 10%
                if current_packet in progress_intervals:
                    percentage = (current_packet / total_packets) * 100
                    print(f"\n[INFO] Progress: {percentage:.0f}% completed ({current_packet}/{total_packets} packets)")

                    # Print unique message if available
                    if final_unique_message:
                        print(f"[INFO] Current decrypted message: {final_unique_message}")

                # Print progress bar
                sys.stdout.write(
                    f"\rProcessing: {current_packet / total_packets * 100:.1f}% [{current_packet}/{total_packets}]")
                sys.stdout.flush()

            # Final status
            print(f"\n\n[INFO] Successfully decrypted {successfully_decrypted}/{total_packets} packets.")
            if final_unique_message:
                print(f"[INFO] Final decrypted message: {final_unique_message}")

        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
        finally:
            print("\n[INFO] Connection closed.")


if __name__ == "__main__":
    tcp_client()
