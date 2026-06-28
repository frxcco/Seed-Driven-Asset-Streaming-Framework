#!/usr/bin/env python3
import os
import time
import sys
import msvcrt  # Native Windows low-level console I/O
from psp_stream_core import XorshiftSeekable

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

    def update_input(self, client_input_vector: list):
        """Injects network-received input vectors into the physics loop."""
        # Prevent the snake from reversing into itself directly
        if [client_input_vector[0] * -1, client_input_vector[1] * -1] != self.direction:
            self.direction = client_input_vector

    def process_frame(self) -> bytes:
        """Advances game logic by one tick and returns an encrypted byte block."""
        self.frame_index += 1
        
        if not self.game_over:
            # Move snake head based on active direction vector
            new_head = [self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1]]
            
            # Boundary collision check (Screen wrapping or Game Over)
            if new_head[0] < 0 or new_head[0] >= self.height or new_head[1] < 0 or new_head[1] >= self.width:
                self.game_over = True
            # Self-collision check
            elif new_head in self.snake:
                self.game_over = True
            else:
                self.snake.insert(0, new_head)
                self.snake.pop()
                self.score += 1

        # Render current frame buffer to raw text layout
        frame_rows = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if [y, x] in self.snake:
                    row += "🟩" if [y, x] == self.snake[0] else "🟢"
                else:
                    row += "░░"
            frame_rows.append(row)
        
        # Build raw metadata payload
        status = "GAME OVER" if self.game_over else "STREAMING ACTIVE"
        video_text = f"--- CORE PSP CLOUD STREAM ({status}) ---\n"
        video_text += f"Frame Index: {self.frame_index} | Score: {self.score}\n\n"
        video_text += "\n".join(frame_rows) + "\n"
        video_text += "========================================================\n"
        video_text += "[Controls]: Use Arrow Keys to play. Press 'ESC' to exit.\n"
        
        raw_bytes = video_text.encode('utf-8')

        # Multi-layer abstraction: Obfuscate the network frame using seekable PRNG phase shift
        noise = self.prng.generate_block_noise(self.frame_index, len(raw_bytes))
        return bytes(b ^ r for b, r in zip(raw_bytes, noise))


class LocalDRMDecoder:
    """Handles real-time stream decoding and stdout flushing."""
    def __init__(self, seed: int):
        self.prng = XorshiftSeekable(seed)

    def render_incoming_bytes(self, frame_idx: int, encrypted_payload: bytes):
        """Decrypts payload in volatile RAM and prints to display hardware."""
        noise = self.prng.generate_block_noise(frame_idx, len(encrypted_payload))
        clean_buffer = bytes(b ^ r for b, r in zip(encrypted_payload, noise))
        
        # Fast console flush
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.stdout.write(clean_buffer.decode('utf-8', errors='ignore'))
        sys.stdout.flush()


def capture_keyboard_input():
    """Reads non-blocking hardware keyboard scans from Windows console."""
    if msvcrt.kbhit():
        key = msvcrt.getch()
        # Check for Escape key
        if key == b'\x1b':
            return "EXIT"
        # Check for Arrow key prefix (0xE0 or 0x00 on Windows)
        if key in (b'\x00', b'\xe0'):
            arrow = msvcrt.getch()
            if arrow == b'H': return [-1, 0] # Up Arrow
            if arrow == b'P': return [1, 0]  # Down Arrow
            if arrow == b'K': return [0, -1] # Left Arrow
            if arrow == b'M': return [0, 1]  # Right Arrow
    return None


# =====================================================================
# RUNTIME EXECUTION PIPELINE
# =====================================================================
if __name__ == "__main__":
    SEED_TOKEN = 999888
    
    server = CloudGameEngine(seed=SEED_TOKEN)
    client = LocalDRMDecoder(seed=SEED_TOKEN)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🔋 Pipeline Sync: Engine & Decoder linked to channel seed.")
    print("🎮 Ready. The stream loop will run indefinitely.")
    input("👉 Press ENTER to mount the real-time stream connection...")

    # Infinite Frame Loop
    while True:
        # 1. Asynchronously capture input from client's physical keyboard
        user_action = capture_keyboard_input()
        
        if user_action == "EXIT":
            print("\nStream session closed by user interaction request.")
            break
        elif isinstance(user_action, list):
            # Send input state over the network simulation
            server.update_input(user_action)

        # 2. Server advances state and pushes encrypted byte frame to network buffer
        network_packet = server.process_frame()

        # 3. Client receives network packet, decrypts via stream index, and outputs video
        client.render_incoming_bytes(server.frame_index, network_packet)

        # Frame rate controller (~15-20 FPS simulation for standard console buffer stability)
        time.sleep(0.07)