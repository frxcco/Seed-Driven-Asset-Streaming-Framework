#!/usr/bin/env python3
import os
import time
from psp_stream_core import PSPStreamEngine

# =====================================================================
# 1. SECRET RETRO GAME SOURCE CODE (Simulated Independent Development)
# =====================================================================
# This is the raw code of the retro snake game that we want to protect.
# It will be compiled into mathematical noise and executed strictly from RAM.
SNAKE_GAME_SOURCE = """
import time
import os
import sys

def run_retro_game():
    # A simple automated retro snake game running directly in the console
    width, height = 20, 10
    snake = [[5, 5], [5, 4], [5, 3]]
    direction = [0, 1] # Start moving right
    
    print("\\n" + "="*45)
    print(" 🎮 LAUNCHING OBFUSCATED RETRO GAME ARCHITECTURE...")
    print("="*45)
    time.sleep(1.5)
    
    for frame in range(15): # Run 15 frames of animation
        # Clear screen based on OS
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"--- SEED-DRIVEN RUNTIME STREAMING (Frame {frame+1}/15) ---")
        
        # Calculate snake movement
        new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
        
        # Mutate direction based on frame count to simulate automated movement
        if frame == 5: direction = [1, 0]   # Move down
        if frame == 10: direction = [0, -1] # Move left
        
        snake.insert(0, new_head)
        snake.pop()
        
        # Render the map frame onto the screen
        for y in range(height):
            row = ""
            for x in range(width):
                if [y, x] in snake:
                    row += "🟩" if [y, x] == snake[0] else "🟢"
                else:
                    row += "░░"
            print(row)
        
        time.sleep(0.3)
        
    print("\\n🚀 SUCCESS: Process gracefully terminated from Volatile RAM.")
run_retro_game()
"""

# =====================================================================
# 2. AUTOMATION & PACKAGING PIPELINE
# =====================================================================
if __name__ == "__main__":
    print("🚀 [Step 1] Simulating Game Studio packaging pipeline...")
    
    # Write the raw code to a temporary file so the engine can process it
    with open("temp_source.py", "w", encoding="utf-8") as f:
        f.write(SNAKE_GAME_SOURCE)
        
    # Invoke your custom PSP Stream Engine to secure the asset using seed 4242
    SECRET_SEED = 4242
    PSPStreamEngine.pack_asset("temp_source.py", "game.psps", seed=SECRET_SEED)
    
    # Purge the unencrypted plaintext source file immediately
    os.remove("temp_source.py")
    print("   ✓ Secure container 'game.psps' created successfully.")
    print("   🗑️ Plaintext file deleted from disk. Only obfuscated binary noise remains.\n")
    
    print("👀 [Inspection Pause] Try opening 'game.psps' with your text editor right now.")
    print("   You will see that the snake code does not exist; it is completely illegible.")
    input("👉 Press ENTER when you are ready to fire up the Client Launcher... ")
    print("\n" + "="*70)
    
    # =====================================================================
    # 3. VOLATILE CLIENT LAUNCHER (App-Level DRM Runtime)
    # =====================================================================
    print("🧠 [Step 2] Initializing Game Launcher Environment...")
    time.sleep(1)
    
    # Mount the custom streaming framework over the protected asset
    streamer = PSPStreamEngine("game.psps")
    print(f"   ✓ Reading binary structure layout from stream ({streamer.total_size} bytes)...")
    
    # In a real system, the remote authentication server would supply the seed over TLS.
    # Here we feed the matching integer seed straight into the seekable PRNG.
    print("   ✓ Synchronizing in-memory decoder state...")
    
    # Extract the entire content directly into a single variable inside volatile RAM.
    # The read_range() method handles all target offsets and decrypts the chunks on-the-fly.
    live_code_in_ram = streamer.read_range(0, streamer.total_size).decode('utf-8')
    streamer.close()
    
    print("🔥 [Step 3] Executing ephemeral code buffer directly from volatile memory...")
    time.sleep(1)
    
    # ZERO-DISK RUNTIME INJECTION:
    # Python's built-in exec() evaluates the decoded string variable entirely inside RAM,
    # pushing instructions straight to the CPU registers. Once the script finishes, 
    # the runtime garbage collector wipes the buffer, leaving absolutely zero trace on the disk.
    exec(live_code_in_ram)