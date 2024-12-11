import socket, json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64, os

class Server:
    def _init_(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.payload = "The quick brown fox jumps over the lazy dog."
        self.keys = self._setup_encryption_keys()
        self.polarization_map = {'00': 0, '01': 1, '10': 2, '11': 3}

    def _setup_encryption_keys(self):
        keys = []
        salt_values = [b'horizontal_salt_000', b'vertical_salt_0001', b'clockwise_salt_002', b'counterclck_salt03']
        for i, salt in enumerate(salt_values):
            key_gen = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(key_gen.derive(f"polarization{i}".encode()))
            keys.append(Fernet(key))
        return keys
    
    def load_file(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        return ''.join(format(byte, '08b') for byte in data)

    def split_into_pairs(self, binary_data):
        return [binary_data[i:i+2] for i in range(0, len(binary_data), 2)]

    def create_encrypted_packet(self, bit_pair):
        key_idx = self.polarization_map[bit_pair]
        encrypted = self.keys[key_idx].encrypt(self.payload.encode())
        return {'encrypted_payload': base64.b64encode(encrypted).decode(), 'packet_index': self.current_packet_index}

    def send_file(self, file_path):
        print(f"Starting to send file: {file_path}")
        binary_data = self.load_file(file_path)
        bit_pairs = self.split_into_pairs(binary_data)
        total_packets = len(bit_pairs)
        client, addr = self.socket.accept()
        print(f"Got connection from {addr}")
        completion = 0
        while completion < 100:
            for i, bits in enumerate(bit_pairs):
                self.current_packet_index = i
                packet = self.create_encrypted_packet(bits)
                client.send(json.dumps(packet).encode())
                completion = float(client.recv(1024).decode())
                print(f"Sent packet {i}/{total_packets}. Client has {completion}%")
                if completion == 100:
                    break
        print("File sent successfully!")
        client.close()

    def run(self, file_path):
        print(f"Starting quantum server on {self.host}:{self.port}")
        try:
            self.send_file(file_path)
        except Exception as e:
            print(f"Oops, something went wrong: {e}")
        finally:
            self.socket.close()

if _name_ == "_main_":
    server = Server()
    server.run("testData.txt")
