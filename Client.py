import socket
import struct
from Crypto.Cipher import AES
from Crypto import keys 
HOST = '127.0.0.1'
PORT = 5555

def decrypt_crumb(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    # Remove padding
    pad_len = plaintext[-1]
    if pad_len <= 16:
        plaintext = plaintext[:-pad_len]
    return plaintext

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print(f"[INFO] Connected to {HOST}:{PORT}")

    data = s.recv(4)
    if not data:
        print("[ERROR] Could not receive total crumbs from server.")
        return

    total_crumbs = struct.unpack('!I', data)[0]
    print(f"[INFO] Expecting {total_crumbs} packets")

    if total_crumbs == 0:
        print("[ERROR] Server sent zero crumbs. Check the input file on server side.")
        s.close()
        return

    decrypted_crumbs = [None] * total_crumbs
    previous_message = ""
    fraction_done = lambda: sum(1 for c in decrypted_crumbs if c is not None) / total_crumbs

    while True:
        for i in range(total_crumbs):
            length_data = s.recv(4)
            if not length_data:
                print("[ERROR] Did not receive expected crumb length from server.")
                s.close()
                return

            length = struct.unpack('!I', length_data)[0]
            ciphertext = s.recv(length)

            if decrypted_crumbs[i] is not None:
                continue

            key = keys[f'{i:02b}']
            plaintext = decrypt_crumb(ciphertext, key)

            if plaintext:
                decrypted_crumbs[i] = plaintext
                print(f"[DEBUG] Decoded crumb {i+1}/{total_crumbs}")

                # Reconstruct the message so far
                current_message = b''.join(c for c in decrypted_crumbs if c is not None).decode('utf-8', errors='ignore')

                # Find the new part of the message
                new_segment = current_message[len(previous_message):]
                print(f"[INFO] New decrypted segment: {new_segment}")

                # Update the previous message
                previous_message = current_message

        frac = fraction_done()
        print(f"[INFO] Progress: {frac * 100:.2f}% completed")

        if frac >= 1.0:
            # Final reconstruction
            reconstructed_message = b''.join(decrypted_crumbs).decode('utf-8', errors='ignore')
            with open('output.txt', 'w', encoding='utf-8') as out_f:
                out_f.write(reconstructed_message)
            print(f"[INFO] Reconstructed Message: {reconstructed_message}")
            break

        # Send fraction back to server
        s.sendall(struct.pack('!d', frac))

    print("[INFO] Connection closed.")
    s.close()

if __name__ == '__main__':
    main()
