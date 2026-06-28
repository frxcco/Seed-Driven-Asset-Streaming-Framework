# Research & Development: Roadmap of PoCs

This document outlines the evolutionary steps for the **Seed-Driven Asset Streaming Framework**. The roadmap focuses on shifting the engine from a functional prototype to a resilient, enterprise-grade distributed system.

---

## 🗺️ Progression Roadmap

| PoC ID | Feature Set | Goal | Complexity |
|:---|:---|:---|:---|
| **PoC-04** | **Delta-Compression Engine** | Optimize bandwidth by streaming only state deltas. | High |
| **PoC-05** | **Session Recovery Handshake** | Enable hot-reconnects without dropping the session. | Medium |
| **PoC-06** | **Multi-Tenant Server** | Support concurrent independent streams in one process. | Medium |
| **PoC-07** | **Dynamic Seed Rotation** | Implement Diffie-Hellman entropy exchange. | Very High |

---

## 🛠️ Functional Specifications

### PoC-04: Delta-Compression Engine
* **Objective:** Reduce throughput from full-frame serialization to delta-updates.
* **Specs:**
  * Implement an internal state comparator in the `CloudGameEngine`.
  * Define a binary protocol for object updates (e.g., `[TYPE][ID][X][Y]`).
  * Modify `ClientDecoder` to maintain a local mirror of the game state and apply patches.

### PoC-05: Session Recovery Handshake
* **Objective:** Ensure persistence against unstable network conditions.
* **Specs:**
  * Client sends the last acknowledged `frame_index` during re-connection.
  * Server utilizes `XorshiftSeekable` to instantly jump to the requested `frame_index` state.
  * Prevent duplicate asset processing or state corruption during sync.

### PoC-06: Multi-Tenant Server
* **Objective:** Scale host infrastructure for multiple simultaneous clients.
* **Specs:**
  * Migrate the server loop from a synchronous structure to an `asyncio` or `threading` model.
  * Instantiate isolated `CloudGameEngine` objects per socket connection.
  * Ensure the PRNG state remains unique to each client's `SEED_TOKEN`.

### PoC-07: Dynamic Seed Rotation
* **Objective:** Maximize security via rotating cryptographic keys.
* **Specs:**
  * Integrate a key-exchange handshake phase before streaming commences.
  * Implement a windowed rotation: re-seed the `Xorshift` generator every *N* frames.
  * Validate that the frame-index continuity remains unbroken across rotations.

---

## 📈 Status
- [ ] **PoC-04**: Pending
- [ ] **PoC-05**: Pending
- [ ] **PoC-06**: Pending
- [ ] **PoC-07**: Pending