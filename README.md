
# Seed-Driven Asset Streaming & Obfuscation Framework

A high-performance, low-latency binary streaming engine designed for distributed environments, cloud gaming, and edge computing. This framework decouples file mass from asset identity, enabling secure content delivery with zero-disk persistence and a constant $O(1)$ memory footprint.

---

## 💡 The Core Architecture Shift

Traditional asset delivery systems (like patches, DLCs, or localization builds) require downloading and caching massive duplicate files for minor differences. 

This framework solves this problem by transforming data distribution into a **computational generation problem**. Instead of shipping a heavy, static asset over the network, the framework streams a compact, mathematically unique mutation key (`.psps`). The runtime then reconstructs the asset chunks **on-the-fly directly into RAM** at CPU execution speeds using a deterministic **Xorshift64 Pseudo-Random Number Generator (PRNG)** bound to an integer seed.



```
   [ Encrypted .psps Stream / Key ]
                 │
                 ▼ (Instant Header Read)
┌───────────────────────────────────────────────┐
│ Extract: 64-bit Seed, Chunk Layout & Metadata │
└───────────────────────────────────────────────┘
                 │
                 ▼ (Zero-Disk I/O Latency)
┌───────────────────────────────────────────────┐
│ CPU synchronizes Xorshift to requested offset │
└───────────────────────────────────────────────┘
                 │
                 ▼ (In-Memory Bitwise Fusion)
RAM Chunks:  [ Deterministic Noise Generator ] ──► 0x3F 0xA2 0x19
                              XOR (⊕)
RAM Chunks:  [ Inbound .psps Payload Buffer ]  ──► 0x7A 0xD4 0x6C
                              │
                              ▼
RAM Stream:  [ Raw Bit-Perfect Asset Output ]  ──► 0x45 0x76 0x75 ("A", "s"...)

```

---

## 🔥 Key Technical Capabilities

### ⚡ Deterministic Random Access ($O(1)$ Seek Time)
Unlike traditional sequential cipher streams, our custom `XorshiftSeekable` engine allows the consumer to fast-forward the PRNG state to any arbitrary byte offset in a split second. The engine skips computing previous states and jumps straight to the required chunk index. This makes it a perfect fit for media players, 3D engines, and large-database lookups.

### 🧠 Constant Memory Footprint ($O(1)$ RAM)
Assets are packed and streamed in fixed, hardware-aligned chunks (defaulting to **64 KB**). Whether you are streaming a 100 KB text block or a 100 GB game map, the local client's memory allocation stays minimal and constant.

### 🔒 Enterprise-Grade In-Memory Obfuscation (Anti-Piracy DRM)
Because the assets are processed chunk-by-chunk in the application's runtime space, **the decrypted, uncompressed file never touches the physical SSD or HDD**. If a third party attempts static disk scraping or data-mining, they will only find mathematically uniform entropy (pure noise). 

---

## 🛠️ Performance Features & Specifications

| Metric | Specification / Architecture |
|---|---|
| **Core PRNG Algorithm** | Xorshift64 (Shift-Rotate Hardware Optimization) |
| **Bitwise Operator** | Symmetric involutory bitwise XOR ($\oplus$) |
| **RAM Complexity** | $O(1)$ — Constrained by chunk capacity bound |
| **Disk I/O Footprint** | $O(1)$ Streaming Read / Zero-Disk footprint on runtime execution |
| **Header Layout** | Big-Endian Network Packed Structure (`Magic` + `ChunkSize` + `TotalSize` + `Seed`) |

---

## 💻 Quickstart (CLI Usage & API)

Run the Python pipeline directly from your terminal to simulate high-speed asset streaming and target offsets:

### 1. Secure & Pack an Asset
Take a raw file and bind its identity structure to a specific mathematical seed (e.g., `999`):
```bash
python3 psp_stream_core.py pack main_video.raw game_asset.psps 999

```

### 2. Stream Arbitrary Byte Chunks

The API lets you instantiate a reader stream and request any precise sub-range of data instantly, without loading the rest of the archive into memory:

```python
from psp_stream_core import PSPStreamEngine

# Initialize the low-overhead stream wrapper
streamer = PSPStreamEngine("game_asset.psps")

# Query a deep block within the file (e.g., seeking to byte 19,000 for 35 bytes)
fragment_buffer = streamer.leer_rango(19000, 35)

print(f"Decrypted Asset Fragment in RAM: {fragment_buffer}")
streamer.cerrar()

```

---

## 🚀 Potential Production Use Cases

* **Dynamic Game Localization / DLCs:** Ship a shared asset skeleton once. Swap the game experience or UI languages on the fly by swapping micro-keys bound to seeds, saving gigabytes of CDN transfer fees.
* **Ephemeral DRM Cloud Loading:** Fetch the seed through a secure TLS channel upon user authentication. Build the executable directly inside protected memory boundaries so it disappears completely when the process exits.
* **WebAssembly (WASM) Edge Assets:** Combine the engine with WASM to spin up ultra-fast asset generation loops within web browsers, decreasing initialization times for web-based applications.

