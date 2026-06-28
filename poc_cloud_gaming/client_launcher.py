#!/usr/bin/env python3
import socket
import sys
import os
import time
import struct
import msvcrt
from core.psp_stream_core import XorshiftSeekable, PSPStreamEngine

class LocalDRMDecoder:
    def __init__(self, seed: int):
        self.prng = XorshiftSeekable(seed)

    def render_incoming_bytes(self, frame_idx: int, encrypted_payload: bytes):
        noise = self.prng.generate_block_noise(frame_idx, len(encrypted_payload))
        clean_buffer = bytes(b ^ r for b, r in zip(encrypted_payload, noise))
        
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write(clean_buffer.decode('utf-8', errors='ignore'))
        sys.stdout.flush()

def capture_keys():
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\x1b': return "EXIT"
        if key in (b'\x00', b'\xe0'):
            arrow = msvcrt.getch()
            if arrow == b'H': return "UP"
            if arrow == b'P': return "DOWN"
            if arrow == b'K': return "LEFT"
            if arrow == b'M': return "RIGHT"
    return None

if __name__ == "__main__":
    SEED_TOKEN = 111222333
    SERVER_IP = '127.0.0.1'  # Change to actual Server IP if testing across different machines
    PORT = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((SERVER_IP, PORT))
    except Exception as e:
        print(f"❌ Connection failed: Unable to reach Cloud host at {SERVER_IP}:{PORT}")
        sys.exit(1)

    decoder = LocalDRMDecoder(seed=SEED_TOKEN)
    frame_counter = 0
    print("🔒 Secured Handshake synced. Tunneling interactive video matrix...")
    time.sleep(1)

    try:
        while True:
            # 1. Listen to hardware keyboard inputs and send vectors upstream immediately
            input_action = capture_keys()
            if input_action:
                client_socket.sendall(f"{input_action}\n".encode('utf-8'))
                if input_action == "EXIT": break

            # 2. Read length prefix header (4 bytes)
            try:
                header = client_socket.recv(4)
                if not header or len(header) < 4: break
                packet_len = struct.unpack(">I", header)[0]
                
                # Read complete obfuscated frame payload chunk
                packet = bytearray()
                while len(packet) < packet_len:
                    chunk = client_socket.recv(packet_len - len(packet))
                    if not chunk: break
                    packet.extend(chunk)
            except Exception:
                break

            # 3. Microsecond local cryptographic collision decode and display refresh
            frame_counter += 1
            decoder.render_incoming_bytes(frame_counter, bytes(packet))

    finally:
        client_socket.close()
        print("\n🔌 Streaming tunnel closed cleanly.")