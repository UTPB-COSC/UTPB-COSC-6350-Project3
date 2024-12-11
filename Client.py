import socket
import json
import base64
import random
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class QuantumClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.expected_payload = "The quick brown fox jumps over the lazy dog."
        self.keys = self._generate_keys()
        self.key_to_bit_pair = { 0: '00', 1: '01', 2: '10', 3: '11' }
        self.decoded_bits = {}
        self.total_packets = 0
        
    def _generate_keys(self):
        keys = []
        salts = [
            b'horizontal_salt_000',
            b'vertical_salt_0001',
            b'clockwise_salt_002',
            b'counterclck_salt03'
        ]
        
        for i, salt in enumerate(salts):
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(f"polarization{i}".encode()))
            keys.append(Fernet(key))
        return keys
    
    def attempt_decrypt(self, encrypted_data):
        key_index = random.randint(0, 3)
        key = self.keys[key_index]
        
        try:
            decrypted_data = key.decrypt(encrypted_data).decode()
            if decrypted_data == self.expected_payload:
                return True, key_index
            return False, None
        except Exception:
            return False, None
    
    def calculate_completion(self):
        if self.total_packets == 0:
            return 0
        return (len(self.decoded_bits) / self.total_packets) * 100
    
    def reconstruct_message(self):
        if not self.decoded_bits:
            return None
        sorted_bits = [self.decoded_bits[i] for i in sorted(self.decoded_bits.keys())]
        binary_data = ''.join(sorted_bits)

        byte_data = bytearray()
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            if len(byte) == 8:  
                byte_data.append(int(byte, 2))
                
        return bytes(byte_data)
    
    def start(self):
        try:
            print(f"Connecting to server at {self.host}:{self.port}")
            self.socket.connect((self.host, self.port))
            
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                packet = json.loads(data.decode())
                encrypted_payload = base64.b64decode(packet['encrypted_payload'])
                packet_index = packet['packet_index']
                
                self.total_packets = max(self.total_packets, packet_index + 1)
                
                if packet_index not in self.decoded_bits:
                    success, key_index = self.attempt_decrypt(encrypted_payload)
                    
                    if success:
                        self.decoded_bits[packet_index] = self.key_to_bit_pair[key_index]
                        print(f"Successfully decoded packet {packet_index}")
                
                completion = self.calculate_completion()
                self.socket.send(str(completion).encode())
                print(f"Current completion: {completion}%")
                
                if completion == 100:
                    break
            
            final_message = self.reconstruct_message()
            if final_message:
                with open('received_file.txt', 'wb') as f:
                    f.write(final_message)
                print("File successfully received and saved as 'received_file.txt'")
            
        except Exception as e:
            print(f"Error during reception: {e}")
        finally:
            self.socket.close()

if __name__ == "__main__":
    client = QuantumClient()
    client.start()