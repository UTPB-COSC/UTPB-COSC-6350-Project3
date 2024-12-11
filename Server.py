import socket
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class QuantumServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host    
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.payload = "The quick brown fox jumps over the lazy dog."
        self.keys = self._generate_keys()
        self.bit_pair_to_key = {'00': 0, '01': 1, '10': 2, '11': 3}
        
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
    
    def read_file(self, filepath):
        with open(filepath, 'rb') as file:
            data = file.read()
        return ''.join(format(byte, '08b') for byte in data)
    
    def get_bit_pairs(self, binary_data):
        return [binary_data[i:i+2] for i in range(0, len(binary_data), 2)]
    
    def encrypt_packet(self, bit_pair):
        key_index = self.bit_pair_to_key[bit_pair]
        encrypted_data = self.keys[key_index].encrypt(self.payload.encode())
        return {
            'encrypted_payload': base64.b64encode(encrypted_data).decode(),
            'packet_index': self.current_packet_index
        }
    
    def transmit_file(self, filepath):
        print(f"Server starting transmission of {filepath}")
        
        binary_data = self.read_file(filepath)
        bit_pairs = self.get_bit_pairs(binary_data)
        total_packets = len(bit_pairs)
        
        client_socket, addr = self.socket.accept()
        print(f"Connection from {addr}")
        
        completion = 0
        while completion < 100:
            for i, bit_pair in enumerate(bit_pairs):
                self.current_packet_index = i
                
                packet = self.encrypt_packet(bit_pair)
                client_socket.send(json.dumps(packet).encode())
                
                completion_data = client_socket.recv(1024).decode()
                completion = float(completion_data)
                
                print(f"Packet {i}/{total_packets} sent. Current completion: {completion}%")
                
                if completion == 100:
                    break
        
        print("File transmission completed successfully")
        client_socket.close()
    
    def start(self, filepath):
        try:
            print(f"Quantum Crypto Server starting on {self.host}:{self.port}")
            self.transmit_file(filepath)
        except Exception as e:
            print(f"Error during transmission: {e}")
        finally:
            self.socket.close()

# Example usage
if __name__ == "__main__":
    server = QuantumServer()
    server.start("test_file.txt")