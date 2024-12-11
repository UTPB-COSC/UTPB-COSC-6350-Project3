import socket, json, base64, random
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class Client:
    def _init_(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.test_message = "The quick brown fox jumps over the lazy dog."
        self.keys = self._setup_encryption_keys()
        self.bit_lookup = {0: '00', 1: '01', 2: '10', 3: '11'}
        self.decoded_packets = {}
        self.packet_count = 0

    def _setup_encryption_keys(self):
        keys = []
        salt_values = [b'horizontal_salt_000', b'vertical_salt_0001', b'clockwise_salt_002', b'counterclck_salt03']
        for i, salt in enumerate(salt_values):
            key_gen = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            key = base64.urlsafe_b64encode(key_gen.derive(f"polarization{i}".encode()))
            keys.append(Fernet(key))
        return keys

    def try_decrypt(self, encrypted_data):
        key_num = random.randint(0, 3)
        key = self.keys[key_num]
        try:
            result = key.decrypt(encrypted_data).decode()
            if result == self.test_message:
                return True, key_num
            return False, None
        except:
            return False, None

    def get_completion_percent(self):
        if self.packet_count == 0:
            return 0
        return (len(self.decoded_packets) / self.packet_count) * 100

    def rebuild_file(self):
        if not self.decoded_packets:
            return None
        ordered_bits = [self.decoded_packets[i] for i in sorted(self.decoded_packets.keys())]
        bit_string = ''.join(ordered_bits)
        file_data = bytearray()
        for i in range(0, len(bit_string), 8):
            byte_bits = bit_string[i:i+8]
            if len(byte_bits) == 8:
                file_data.append(int(byte_bits, 2))
        return bytes(file_data)

    def run(self):
        print(f"Connecting to quantum server at {self.host}:{self.port}")
        try:
            self.socket.connect((self.host, self.port))
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                packet = json.loads(data.decode())
                encrypted_data = base64.b64decode(packet['encrypted_payload'])
                packet_num = packet['packet_index']
                self.packet_count = max(self.packet_count, packet_num + 1)
                if packet_num not in self.decoded_packets:
                    worked, key_num = self.try_decrypt(encrypted_data)
                    if worked:
                        self.decoded_packets[packet_num] = self.bit_lookup[key_num]
                        print(f"Got packet {packet_num}!")
                progress = self.get_completion_percent()
                self.socket.send(str(progress).encode())
                print(f"Progress: {progress}%")
                if progress == 100:
                    break
            final_data = self.rebuild_file()
            if final_data:
                with open('receivedData.txt', 'wb') as f:
                    f.write(final_data)
                print("All done! Saved file as 'receivedData.txt'")
        except Exception as e:
            print(f"Oops, something went wrong: {e}")
        finally:
            self.socket.close()

if _name_ == "_main_":
    client = Client()
    client.run()
