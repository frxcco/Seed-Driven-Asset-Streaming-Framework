import socket
import struct
import time
import threading
from core.psp_stream_core import XorshiftSeekable
from poc_cloud_gaming.delta_protocol import DeltaPacker

class DeltaServer:
    def __init__(self, seed, host='127.0.0.1', port=5000):
        self.seed = seed
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.direction = (1, 0)
        print(f"Servidor iniciado en {host}:{port}. Esperando cliente...")

    def run(self, game_logic_func):
        conn, _ = self.sock.accept()
        print("Cliente conectado.")
        conn.send(struct.pack("I", self.seed))
        self.prng = XorshiftSeekable(self.seed)
        self.frame_index = 0

        # Hilo para recibir comandos del cliente
        threading.Thread(target=self.listen_input, args=(conn,), daemon=True).start()

        while True:
            updates = game_logic_func(self.direction)
            for obj_id, x, y in updates:
                packet = DeltaPacker.pack_delta(obj_id, x, y)
                noise = self.prng.generate_block_noise(self.frame_index, 3)
                conn.sendall(bytes(b ^ r for b, r in zip(packet, noise)))
                self.frame_index += 1
            time.sleep(0.1)

    def listen_input(self, conn):
        while True:
            try:
                raw_key = conn.recv(1)
                if not raw_key: break
                key = raw_key.decode('ascii', errors='ignore').lower()
                if key == 'w': self.direction = (0, -1)
                elif key == 's': self.direction = (0, 1)
                elif key == 'a': self.direction = (-1, 0)
                elif key == 'd': self.direction = (1, 0)
            except: 
                break