#!/usr/bin/env python3
import socket
import time
import random
import struct
from core.psp_stream_core import XorshiftSeekable, PSPStreamEngine

class CloudGameEngine:
    """
    Core Cloud Game Engine Executor.
    Manages infinite game state, processes real-time user inputs,
    and outputs encrypted video buffers frame-by-frame.
    """
    def __init__(self, seed: int, width: int = 20, height: int = 10):
        self.prng = XorshiftSeekable(seed)
        self.width = width
        self.height = height
        self.snake = [[5, 5], [5, 4], [5, 3]]
        self.direction = [0, 1]  # Initial vector: Right
        self.frame_index = 0
        self.score = 0
        self.game_over = False
        # Spawn the first random apple safely
        self.apple = [random.randint(0, self.height-1), random.randint(0, self.width-1)]

    def update_input(self, action: str):
        """Injects network-received input strings into the physics loop."""
        vectors = {'UP': [-1, 0], 'DOWN': [1, 0], 'LEFT': [0, -1], 'RIGHT': [0, 1]}
        if action in vectors:
            new_dir = vectors[action]
            # Prevent the snake from reversing directly into its own neck
            if [new_dir[0] * -1, new_dir[1] * -1] != self.direction:
                self.direction = new_dir

    def process_frame(self) -> bytes:
        """Advances game logic by one tick and returns an encrypted byte block."""
        self.frame_index += 1
        
        if not self.game_over:
            # Calculate next step displacement
            new_head = [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]]
            
            # Boundary collision checks
            if new_head[0] < 0 or new_head[0] >= self.height or new_head[1] < 0 or new_head[1] >= self.width:
                self.game_over = True
            # Self collision check
            elif new_head in self.snake:
                self.game_over = True
            else:
                self.snake.insert(0, new_head)
                
                # Check for item consumption (Apple trigger mechanics)
                if new_head == self.apple:
                    self.score += 10
                    # Relocate apple to a clean grid position
                    while True:
                        self.apple = [random.randint(0, self.height-1), random.randint(0, self.width-1)]
                        if self.apple not in self.snake:
                            break
                else:
                    self.snake.pop()

        # Render layout matrix onto virtual buffer
        frame_rows = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if [y, x] in self.snake:
                    row += "🟩" if [y, x] == self.snake[0] else "🟢"
                elif [y, x] == self.apple:
                    row += "🍎"
                else:
                    row += "░░"
            frame_rows.append(row)
        
        # Format terminal payload metadata string
        status = "GAME OVER" if self.game_over else "STREAMING ACTIVE"
        video_text = f"--- PSP CORE NETWORK STREAM ({status}) ---\n"
        video_text += f"Frame Index: {self.frame_index} | Score: {self.score}\n\n"
        video_text += "\n".join(frame_rows) + "\n"
        video_text += "========================================================\n"
        video_text += "[Controls]: Arrow Keys to play. Press 'ESC' to drop link.\n"
        
        raw_bytes = video_text.encode('utf-8')
        
        # Core Algorithm obfuscation layer using dynamic frame token step
        noise = self.prng.generate_block_noise(self.frame_index, len(raw_bytes))
        return bytes(b ^ r for b, r in zip(raw_bytes, noise))


if __name__ == "__main__":
    SEED_TOKEN = 111222333
    HOST = '0.0.0.0'  # Listen across all available interface sockets
    PORT = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    print(f"📡 Cloud Server boot complete. Listening on port {PORT}...")
    
    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"🔌 Secure pipeline connection established from: {addr}")
            
            engine = CloudGameEngine(seed=SEED_TOKEN)
            conn.setblocking(False)  # Unblock network stream I/O operations
            
            while True:
                # 1. Non-blocking retrieval of client command tokens
                try:
                    data = conn.recv(1024).decode('utf-8').strip()
                    if data == "EXIT": 
                        break
                    if data: 
                        engine.update_input(data)
                except BlockingIOError:
                    pass  # No data pushed from client during this tick interval
                except Exception:
                    break

                # 2. Advance ticks and secure layout payload via core algorithm
                packet = engine.process_frame()
                
                # 3. Encapsulate and transmit frame through socket tunnel
                try:
                    # Packet layout structure header: [ 4-Byte Payload Length Info (Big-Endian) ] + [ Obfuscated Chunks ]
                    conn.sendall(struct.pack(">I", len(packet)) + packet)
                except BlockingIOError:
                    pass  # Network buffers full, drop synchronization packet frame
                except Exception:
                    break

                # Self-destruct socket instance safely on hardware execution failure
                if engine.game_over:
                    time.sleep(1.0)  # Allow final Game Over screen state to sync to the client UI
                    break

                time.sleep(0.15)
                
            conn.close()
            print("❌ Client disconnected. Resetting host pipeline container...\n")
            
    except KeyboardInterrupt:
        print("\nShutting down core host infrastructure gracefully.")
    finally:
        server_socket.close()