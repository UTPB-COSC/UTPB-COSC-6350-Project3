import socket
import random
from Crypto import *

# Constants
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555


def tcp_client():
    """Connect to server and receive/decrypt packets"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"[INFO] Connected to {SERVER_HOST}:{SERVER_PORT}")

            # Receive total packets count from server
            total_packets_str = client_socket.recv(1024).decode()
            total_packets = int(total_packets_str)
            client_socket.sendall(b'ACK')  # Acknowledge receipt of total packets

            successfully_decrypted = 0
            failed_attempts = {}

            # Original message
            original_message = "The quick brown fox jumps over the lazy dog."
            words = original_message.split()

            # Tracking for unique word selection
            available_words = words.copy()
            reconstructed_words = []
            last_progress_milestone = 0

            print(f"[INFO] Expecting {total_packets} packets")

            while True:
                encrypted_packet = client_socket.recv(1024)

                if not encrypted_packet or encrypted_packet == b'END':
                    # Final reconstruction
                    print("\n[INFO] End of transmission received.")
                    print("[INFO] Progress: 100% completed")
                    full_message = " ".join(original_message.split())
                    print(f"[INFO] Final reconstructed message: {full_message}")
                    break

                # Try decryption with each key
                key_attempts = list(keys.values())
                packet_number = successfully_decrypted
                key_attempts_failed = failed_attempts.get(packet_number, [])

                decryption_successful = False
                for key in key_attempts:
                    if key in key_attempts_failed:
                        continue

                    try:
                        decrypted_message = aes_decrypt(encrypted_packet, key)
                        if decrypted_message == "The quick brown fox jumps over the lazy dog.":
                            client_socket.sendall(b'ACK')
                            successfully_decrypted += 1
                            decryption_successful = True

                            # Calculate current progress percentage
                            current_progress = (successfully_decrypted / total_packets) * 100

                            # Progress milestones with unique random words
                            progress_milestones = [25, 50, 75]
                            for milestone in progress_milestones:
                                if current_progress >= milestone and last_progress_milestone < milestone:
                                    if available_words:
                                        # Randomly select a unique word not yet used
                                        new_word = random.choice(available_words)
                                        reconstructed_words.append(new_word)
                                        available_words.remove(new_word)

                                        print(
                                            f"\n[INFO] Progress: {milestone}% completed ({successfully_decrypted}/{total_packets} packets)")
                                        print(f"[INFO] Current reconstructed segment: {' '.join(reconstructed_words)}")
                                        last_progress_milestone = milestone
                                    break

                            break
                    except Exception:
                        key_attempts_failed.append(key)

                if not decryption_successful:
                    client_socket.sendall(b'NACK')
                    failed_attempts[packet_number] = key_attempts_failed

            print(f"\n[INFO] Successfully decrypted {successfully_decrypted}/{total_packets} packets.")

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            print("[INFO] Connection closed.")


if __name__ == "__main__":
    tcp_client()