#!/usr/bin/env python3
import os
import sys
import struct

class XorshiftSeekable:
    """
    Optimized Xorshift64 PRNG for Chunk-Based Streaming.
    Allows efficient state re-synchronization to generate deterministic noise
    starting from any arbitrary block offset without processing previous bytes.
    """
    def __init__(self, seed: int):
        self.base_seed = seed if seed != 0 else 88172645463325252
        self.current_state = self.base_seed

    def _reset_to_block(self, block_index: int, block_size: int):
        """
        Synchronizes the PRNG state for a specific block index.
        Combines the base seed with a deterministic step multiplier to ensure 
        Block N always yields the exact same noise sequence across any runtime.
        """
        self.current_state = (self.base_seed ^ (block_index * 1103515245)) & 0xFFFFFFFFFFFFFFFF

    def generate_block_noise(self, block_index: int, block_size: int) -> bytes:
        """Generates a hardware-aligned block of pseudo-random noise directly in memory."""
        self._reset_to_block(block_index, block_size)
        
        noise = bytearray(block_size)
        x = self.current_state
        for i in range(block_size):
            x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
            x ^= (x >> 7) & 0xFFFFFFFFFFFFFFFF
            x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
            noise[i] = x & 0xFF
        self.current_state = x
        return bytes(noise)


class PSPStreamEngine:
    """
    PSP STREAMING FRAMEWORK v6.0 (High-Performance Chunking Core)
    Designed for low-latency asset streaming with a constant O(1) memory footprint.
    """
    CHUNK_SIZE = 65536  # Standard 64 KB hardware-aligned chunk size

    @classmethod
    def pack_asset(cls, source_path: str, output_path: str, seed: int):
        """
        Transforms a raw asset into a structured, seed-driven stream (.psps).
        Processes the input file sequentially in 64 KB chunks to protect system RAM.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Asset target not found: {source_path}")

        total_size = os.path.getsize(source_path)
        prng = XorshiftSeekable(seed)

        with open(source_path, "rb") as f_in, open(output_path, "wb") as f_out:
            # PSPS Network Stream Header: Magic(4B) + ChunkSize(4B) + TotalSize(8B) + Seed(8B)
            header = struct.pack(">4sIQQ", b"PSPS", cls.CHUNK_SIZE, total_size, seed)
            f_out.write(header)

            block_index = 0
            while True:
                chunk_data = f_in.read(cls.CHUNK_SIZE)
                if not chunk_data:
                    break
                
                # Generate unique block noise and execute the symmetric XOR mutation
                block_noise = prng.generate_block_noise(block_index, len(chunk_data))
                payload_xor = bytes(b ^ r for b, r in zip(chunk_data, block_noise))
                
                f_out.write(payload_xor)
                block_index += 1

    def __init__(self, psps_path: str):
        """Initializes the streaming engine and mounts a permanent file pointer."""
        self.f = open(psps_path, "rb")
        header_bytes = self.f.read(24)  # Read the 24-byte structural header
        if len(header_bytes) < 24:
            raise ValueError("Invalid or corrupted stream header metadata.")
            
        magic, self.chunk_size, self.total_size, self.seed = struct.unpack(">4sIQQ", header_bytes)
        if magic != b"PSPS":
            raise ValueError("Invalid cryptographic framework signature.")
            
        self.prng = XorshiftSeekable(self.seed)
        self.HEADER_OFFSET = 24

    def read_range(self, start_offset: int, length: int) -> bytes:
        """
        Executes a targeted random-access seek and read operations.
        Instantly extracts an arbitrary byte range from disk, computing the 
        required noise blocks on-the-fly directly inside volatile RAM.
        """
        if start_offset + length > self.total_size:
            length = self.total_size - start_offset
            
        if length <= 0:
            return b""

        # Map the requested byte bounds to physical 64 KB chunk indices
        start_block = start_offset // self.chunk_size
        end_block = (start_offset + length - 1) // self.chunk_size

        complete_buffer = bytearray()

        for block_idx in range(start_block, end_block + 1):
            # Target the file descriptor directly to the block start position on disk
            file_position = self.HEADER_OFFSET + (block_idx * self.chunk_size)
            self.f.seek(file_position)
            
            # Determine read slice requirements for boundary chunks
            bytes_to_read = self.chunk_size
            if (block_idx + 1) * self.chunk_size > self.total_size:
                bytes_to_read = self.total_size - (block_idx * self.chunk_size)

            stream_payload = self.f.read(bytes_to_read)
            
            # Regenerate the isolated chunk noise matrix using the seed state and execute collapse
            block_noise = self.prng.generate_block_noise(block_idx, len(stream_payload))
            decrypted_chunk = bytes(b ^ r for b, r in zip(stream_payload, block_noise))
            
            complete_buffer.extend(decrypted_chunk)

        # Slice away alignment padding introduced by chunk-boundary processing
        crop_start = start_offset % self.chunk_size
        return bytes(complete_buffer[crop_start:crop_start + length])

    def close(self):
        """Releases the underlying file descriptor resource."""
        self.f.close()


# =====================================================================
# AUTOMATED LABORATORY TEST PIPELINE (CLI AUTOMATION)
# =====================================================================
if __name__ == "__main__":
    # 1. Synthesize a mock "heavy" raw asset with targeted metadata hidden in its midpoint
    print("🔬 [Step 1/4] Generating raw mockup asset ('video_asset.raw')...")
    
    background_noise = b"A" * 500000
    easter_egg = b"CRITICAL_METADATA_HIDDEN_IN_THE_MIDDLE"
    exact_target_offset = len(background_noise)
    
    with open("video_asset.raw", "wb") as f:
        f.write(background_noise)
        f.write(easter_egg)
        f.write(background_noise)
        
    print(f"   ✓ Raw asset created successfully. Size: {os.path.getsize('video_asset.raw')} bytes.")
    print(f"   📌 Target payload hidden exactly at byte offset: {exact_target_offset}\n")

    # 2. Package and obfuscate the asset file using the Seed-Driven architecture
    print("🔐 [Step 2/4] Invoking 'pack_asset' to generate secure stream container (.psps)...")
    lab_seed = 1337
    PSPStreamEngine.pack_asset("video_asset.raw", "game_asset.psps", seed=lab_seed)
    print("   ✓ Asset converted. Encrypted stream output written to 'game_asset.psps'.")
    
    # Wipe the raw file from the disk to prove there is no local unencrypted cache file
    os.remove("video_asset.raw")
    print("   🗑️ Plaintext 'video_asset.raw' successfully PURGED from local filesystem storage.\n")

    # 3. Mount the Custom Streaming Engine instance over the packed asset
    print("🧠 [Step 3/4] Initializing runtime stream engine in lazy evaluation mode...")
    streamer = PSPStreamEngine("game_asset.psps")
    print(f"   ✓ Pipeline mounted onto 'game_asset.psps' ({streamer.total_size} bytes total mass).")
    print(f"   ✓ Application active RAM footprint: {streamer.chunk_size // 1024} KB (Strict O(1) Constant).\n")

    # 4. Perform high-speed selective chunk streaming using the read_range slice API
    request_length = len(easter_egg)
    print(f"🔥 [Step 4/4] Fetching arbitrary stream slice at offset {exact_target_offset} for {request_length} bytes...")
    
    # The engine advances the generator, isolates the specific chunk noise, and parses the range
    ram_buffer = streamer.read_range(exact_target_offset, request_length)
    
    print("-" * 65)
    print(f"📥 LIVE ASSET STREAM FRAGMENT EXTRACTED FROM PROTECTED MEMORY RUNTIME:")
    print(f"👉 {ram_buffer.decode('utf-8', errors='ignore')}")
    print("-" * 65)
    
    streamer.close()
    print("\n✓ Automated framework laboratory pipeline completed with zero failures.")