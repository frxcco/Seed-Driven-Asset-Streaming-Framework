#!/usr/bin/env python3
import os
import time
import struct
from psp_stream_core import XorshiftSeekable

class CloudGameServer:
    """
    Simulates a Cloud Gaming Edge Server.
    Processes the game engine loop, renders frames to bytes, and encrypts
    each frame video chunk on-the-fly using a dynamic synchronization seed.
    """
    def __init__(self, seed: int, width: int = 20, height: int = 10):
        self.prng = XorshiftSeekable(seed)
        self.width = width
        self.height = height
        self.snake = [[5, 5], [5, 4], [5, 3]]
        self.direction = [0, 1]  # Initial movement: Right
        self.frame_counter = 0

    def process_next_frame_chunk(self) -> bytes:
        """
        Game Engine Tick: Updates game state, captures the text-based video frame,
        and mutates the chunk bytes using deterministic stream cipher noise.
        """
        self.frame_counter += 1
        
        # 1. Update Game Logic (AI Snake pathing manipulation)
        if self.frame_counter == 8:  self.direction = [1, 0]   # Move Down
        if self.frame_counter == 14: self.direction = [0, -1]  # Move Left
        if self.frame_counter == 22: self.direction = [-1, 0]  # Move Up
        
        new_head = [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]]
        self.snake.insert(0, new_head)
        self.snake.pop()

        # 2. Render Virtual Video Buffer to string layout
        frame_rows = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if [y, x] in self.snake:
                    row += "🟩" if [y, x] == self.snake[0] else "🟢"
                else:
                    row += "░░"
            frame_rows.append(row)
        
        raw_frame_string = f"--- NVIDIA CLOUD STREAMING ACTIVE (Frame {self.frame_counter}/30) ---\n"
        raw_frame_string += "\n".join(frame_rows) + "\n"
        raw_frame_string += "========================================================\n"
        raw_frame_bytes = raw_frame_string.encode('utf-8')

        # 3. Stream Obfuscation: Mutate frame bytes using unique noise per block index
        # This guarantees that even if frames look identical, their network bytes are entirely different.
        frame_noise = self.prng.generate_block_noise(self.frame_counter, len(raw_frame_bytes))
        encrypted_network_chunk = bytes(b ^ r for b, r in zip(raw_frame_bytes, frame_noise))
        
        return encrypted_network_chunk


class LocalClientDisplay:
    """
    Simulates a 'dumb' client application (like an NVIDIA Shield or thin-client App).
    It holds zero game logic. It simply pulls raw encrypted network chunks,
    re-aligns the PRNG phase via seed, and collapses the bytes directly into the GPU/Display buffer.
    """
    def __init__(self, seed: int):
        self.prng = XorshiftSeekable(seed)

    def receive_and_render_chunk(self, frame_index: int, encrypted_chunk: bytes):
        """Decrypts the incoming binary network chunk in RAM and prints to display."""
        # Synchronize local PRNG state to matching frame network index
        frame_noise = self.prng.generate_block_noise(frame_index, len(encrypted_chunk))
        
        # In-memory bitwise fusion translation
        decrypted_video_buffer = bytes(b ^ r for b, r in zip(encrypted_chunk, frame_noise))
        
        # Flush stdout and display clean video frame
        os.system('cls' if os.name == 'nt' else 'clear')
        print(decrypted_video_buffer.decode('utf-8', errors='ignore'))


# =====================================================================
# CLOUD GAMING RUNTIME SIMULATION PIPELINE
# =================────────────────────
if __name__ == "__main__":
    # SHARED SESSION SECURITY HANDSHAKE
    # In production, this token is dynamically negotiated via Secure TLS upon login.
    SESSION_STREAM_SEED = 777123 
    
    print("🌐 [Cloud Setup] Spawning remote game engine container instance...")
    server = CloudGameServer(seed=SESSION_STREAM_SEED)
    
    print("🖥️ [Client Setup] Initializing local hardware video decoder...")
    client = LocalClientDisplay(seed=SESSION_STREAM_SEED)
    
    input("\n🎮 Session authenticated. Press ENTER to start streaming from Cloud Edge... ")
    
    # EMULATE 30 FPS / FRAMES CHUNK STREAM
    total_stream_frames = 30
    for current_frame in range(1, total_stream_frames + 1):
        
        # 1. Server generates the video frame and encrypts the chunk payload
        network_payload_chunk = server.process_next_frame_chunk()
        
        # --- AT THIS POINT: network_payload_chunk is traveling over the network ---
        # If an attacker sniffs the network packets, they will only see randomized bitwise noise.
        # --------------------------------------------------------------------------
        
        # 2. Client receives the raw byte block, decrypts it on-the-fly, and pushes to terminal display
        client.receive_and_render_chunk(current_frame, network_payload_chunk)
        
        # Simulate video transmission/rendering frame interval latency (300ms per step)
        time.sleep(0.3)
        
    print("🔌 Stream connection dropped: Session closed by cloud host.")