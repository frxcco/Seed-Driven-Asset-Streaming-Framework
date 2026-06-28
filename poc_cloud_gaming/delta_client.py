# delta_client.py
import socket, struct, os, threading, msvcrt
from core.psp_stream_core import XorshiftSeekable
from poc_cloud_gaming.delta_protocol import DeltaPacker

class DeltaClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        seed = struct.unpack("I", self.sock.recv(4))[0]
        self.prng = XorshiftSeekable(seed)
        self.frame_index = 0
        self.grid = [[DeltaPacker.OBJ_EMPTY for _ in range(20)] for _ in range(10)]
        for i in range(20): self.grid[0][i] = self.grid[9][i] = DeltaPacker.OBJ_WALL

    def run(self):
        threading.Thread(target=self.net_loop, daemon=True).start()
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Si es una tecla especial (0xe0), ignoramos el siguiente byte
                if key in (b'\xe0', b'\x00'): msvcrt.getch() 
                else: self.sock.send(key)
            
            print("\033[H", end="")
            for row in self.grid:
                print("".join(['  ' if c==0 else '🟩' if c==1 else '🍎' if c==2 else '🧱' for c in row]))

    def net_loop(self):
        while True:
            try:
                data = self.sock.recv(3)
                if not data: break
                noise = self.prng.generate_block_noise(self.frame_index, 3)
                obj_id, x, y = DeltaPacker.unpack_delta(bytes(b ^ r for b, r in zip(data, noise)))
                # Seguridad: Verificar límites antes de asignar
                if 0 <= y < 10 and 0 <= x < 20:
                    self.grid[y][x] = obj_id
                self.frame_index += 1
            except: break