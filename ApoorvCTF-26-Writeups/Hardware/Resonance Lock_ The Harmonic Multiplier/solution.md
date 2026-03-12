# Solution Guide — Resonance Lock: The Harmonic Multiplier

> **SPOILER WARNING** — This is the full step-by-step walkthrough for solving
> the Harmonix-7 CTF challenge.  Do not read this until you want the answer.

---

## Table of Contents

1. [Understanding the Challenge](#1-understanding-the-challenge)
2. [Reverse-Engineering the Protocol](#2-reverse-engineering-the-protocol)
3. [Phase 1: Achieving Baud Lock](#3-phase-1-achieving-baud-lock)
4. [Phase 2: Sending the Multiplier Command](#4-phase-2-sending-the-multiplier-command)
5. [Phase 3: Computing the Flag Locally](#5-phase-3-computing-the-flag-locally)
6. [Anti-Tamper: What NOT to Do](#6-anti-tamper-what-not-to-do)
7. [Complete Solution Script](#7-complete-solution-script)
8. [Troubleshooting Common Issues](#8-troubleshooting-common-issues)
9. [Key Takeaways](#9-key-takeaways)

---

## 1. Understanding the Challenge

The challenge emulates a fictional **Harmonix-7 SoC** that speaks UART over TCP.
The chip has three states:

```
WAIT  ──(0xCA)──►  CALIBRATE  ──(5 good PPM readings)──►  LOCKED
```

**The pain point:** The server uses `time.perf_counter_ns()` to measure exactly
how long it takes you to send calibration bytes.  Your timing must match a baud
rate of **2,345,679** within ±1,000 PPM (±0.1%).  Once locked, sending a valid
multiplier command returns the fixed flag `apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}`.

### Key constants (from config.py / README):

| Constant          | Value                      |
|-------------------|----------------------------|
| Target baud       | 2,345,679                  |
| Frame bits        | 10 (8N1)                   |
| Calibration byte  | 0x55                       |
| Calibration count | 64 bytes                   | 
| PPM tolerance     | ±1,000                     |
| Lock requirement  | 5 consecutive good         |
| Supercap timeout  | 45 seconds                 |
| Modulus magic      | 0x1337C0DE1337C0DE (legacy, unused) |
| XOR mask          | 0xC0FFEE (legacy, unused)            |
| Fixed flag        | `apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}` |
| Tamper fuse       | Permanent per session      |
| Tamper trigger    | Dump opcodes / byte floods |

---

## 2. Reverse-Engineering the Protocol

### Step 2.1 — Connect and observe

```bash
nc 127.0.0.1 1337
```

You see **nothing**.  The server is in WAIT mode and sends no banner to
the player.  This tells you it's a binary protocol, not text-based.

### Step 2.2 — Identify the state machine

From the README/challenge description, the protocol is:

1. **WAIT** → Send `0xCA` to enter calibration
2. **CALIBRATE** → Send 64 × `0x55` with correct timing
3. **LOCKED** → Send `0xAA` + 128-byte payload to get the flag

### Step 2.3 — Understand timing measurement

The server measures time like this (from device.py source or by deduction):

```
1. Player sends first 0x55 → server records t0
2. Player sends remaining 63 × 0x55 → server records t1 after all arrive
3. elapsed = t1 - t0
4. expected = 63 bytes × 10 bits × (1/2345679) seconds
5. PPM error = ((elapsed - expected) / expected) × 1,000,000
```

**Critical insight:** The server measures the last **63 bytes**, not all 64.
The first 0x55 is the timing trigger.

---

## 3. Phase 1: Achieving Baud Lock

### Step 3.1 — Why `time.sleep()` won't work

`time.sleep()` on Linux typically has ~1ms granularity.  At 2,345,679 baud with
10-bit frames, one byte takes:

```
byte_time = 10 / 2,345,679 = 4.263 µs ≈ 4263 ns
```

That's 4.2 microseconds per byte — you need **nanosecond-level** timing.
`time.sleep()` is about 1000× too coarse.

### Step 3.2 — Use a busy-wait spin loop

```python
import time

def precise_sleep_ns(target_ns: int):
    """Spin-wait for exact nanosecond delays."""
    deadline = time.perf_counter_ns() + target_ns
    while time.perf_counter_ns() < deadline:
        pass
```

### Step 3.3 — Calculate the inter-byte delay

For baud rate B with 10-bit frames:

```python
TARGET_BAUD = 2345679
FRAME_BITS = 10
byte_time_ns = int((FRAME_BITS * 1_000_000_000) / TARGET_BAUD)
# byte_time_ns = 4263 ns (approximately)
```

### Step 3.4 — Send the calibration burst

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 1337))
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # CRITICAL!

# Enter CALIBRATE mode
sock.sendall(bytes([0xCA]))
time.sleep(0.01)  # Let server process state change

# Send first 0x55 (starts server timer)
sock.sendall(bytes([0x55]))

# Send remaining 63 × 0x55 with precise timing
for i in range(63):
    precise_sleep_ns(byte_time_ns)
    sock.sendall(bytes([0x55]))
```

### Step 3.5 — Read and parse the PPM error

```python
resp = b""
sock.settimeout(5.0)
while b"\n" not in resp:
    resp += sock.recv(64)
line = resp.decode().strip()
print(line)  # e.g., "ERR:+00042" or "LOCKED"
```

### Step 3.6 — Iterate until LOCKED

Repeat the calibration cycle.  Each time:
1. Send `0xCA` (re-enter CALIBRATE)
2. Send 64 × `0x55` with precise timing
3. Read the `ERR:` response
4. If `|PPM| ≤ 200`, it counts as a "good" reading
5. After **5 consecutive** good readings → `LOCKED`

**Important:** If any reading exceeds ±1,000 PPM, the counter resets to 0.
You need 5 *consecutive* good ones.

### Step 3.7 — Tuning tips

- **TCP_NODELAY** is essential — Nagle's algorithm will batch your tiny
  sends into one packet, destroying your timing.
- **CPU affinity** helps — pin your process to one core:
  ```bash
  taskset -c 0 python solution.py
  ```
- **Run locally** if possible — network latency between machines adds jitter.
  Connect from the same machine or Docker network.
- Don't run other heavy processes — CPU scheduling jitter is your enemy.

---

## 4. Phase 2: Sending the Multiplier Command

### Step 4.1 — Prepare operands

You need two 64-byte (512-bit) big-endian integers.  Simple test values work:

```python
A = (7).to_bytes(64, "big")   # A = 7
B = (6).to_bytes(64, "big")   # B = 6
```

### Step 4.2 — Send the MULT command

```python
# 0xAA + 64 bytes A + 64 bytes B = 129 bytes total
payload = bytes([0xAA]) + A + B
sock.sendall(payload)
```

### Step 4.3 — Read the flag

```python
resp = b""
sock.settimeout(10.0)
while b"\n" not in resp:
    resp += sock.recv(256)
flag_line = resp.decode().strip()
print(flag_line)  # "FLAG:abcdef0123456789..."
```

---

## 5. Phase 3: Verifying the Flag

The flag is now **fixed**.  If you solved the challenge correctly (achieved
LOCKED and sent a valid MULT command), the server always returns:

```
FLAG:apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}
```

The flag no longer depends on baud timing precision.  As long as your timing
is within ±1,000 PPM for 5 consecutive readings, you get the correct flag.

**If you get a different/garbled flag**, the tamper fuse was blown during
your session.  Disconnect and reconnect.

---

## 6. Anti-Tamper: What NOT to Do

> **⚠ CRITICAL: Read this BEFORE you start probing the service.**

The Harmonix-7 contains a Hardware Security Module (HSM) with a tamper fuse.
If you trip it, your **entire TCP session** is permanently corrupted.

### What triggers it:

1. **JTAG/SWD commands** — Sending bytes like `0xFF` (JTAG reset), `0x00`
   (all-zeros probe), `0xA5` (SWD preamble), `0xFE` (SWD line reset)
2. **Flash memory read opcodes** — `0x03` (SPI Read), `0x0B` (Fast Read),
   `0x9F` (JEDEC ID), `0x90` (Manufacturer ID), `0x4B` (Unique ID), etc.
3. **Flash write/erase opcodes** — `0x06` (Write Enable), `0x20` (Sector Erase),
   `0xD8` (Block Erase), `0xC7` (Chip Erase), `0x02` (Page Program)
4. **Byte flooding** — Sending more than ~20 invalid bytes within 2 seconds
5. **Any invalid byte** in any state accumulates tamper score

### What happens:

- Each suspicious byte adds to a **tamper score** (dump opcodes score 25
  points, generic invalid bytes score 5, flood detection adds 10)
- At **50 points**, the tamper fuse blows
- You get **one** warning: `ERR:HSM_TAMPER_FUSE_BLOWN`
- After that: **silence**.  The chip still works, calibration still appears
  to succeed, you still get `LOCKED` and flags — but a random drift of
  **5,000–50,000 PPM** is permanently injected into all measurements.
  Every flag will be garbage.  There is no indication this is happening.
- **There is no recovery within the session.**  You must disconnect and
  start a fresh TCP connection.

### How to avoid it:

- **Only send the three valid opcodes**: `0xCA` (calibrate), `0x55` (pattern),
  `0xAA` (multiply)
- **Do NOT probe for hidden commands** — there are none
- **Do NOT try to brute-force** by sending random bytes
- **Do NOT use tools like `nmap`, protocol scanners, or fuzzers** on the port
- If you need to retry, simply send `0xCA` again to re-enter calibration

### How to detect if you've been tampered:

- You saw `ERR:HSM_TAMPER_FUSE_BLOWN` at any point
- Your flags don't match local calculation even though PPM looks "good"
- The ERR values seem weirdly offset from what you'd expect
- **Fix: disconnect and reconnect**

---

## 7. Complete Solution Script

Save this as `solution.py` and run it:

```python
#!/usr/bin/env python3
"""
Full solver for Resonance Lock: The Harmonic Multiplier
"""

import socket
import time
import sys

# ── Configuration ──────────────────────────────────────────────────
HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1337

TARGET_BAUD    = 2345679
FRAME_BITS     = 10
BYTE_TIME_NS   = int((FRAME_BITS * 1_000_000_000) / TARGET_BAUD)

MODULUS_MAGIC  = 0x1337C0DE1337C0DE  # legacy, unused
FLAG_XOR_MASK  = 0xC0FFEE             # legacy, unused
FIXED_FLAG     = "apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}"


def precise_sleep_ns(ns: int):
    """Busy-wait spin loop for nanosecond precision."""
    deadline = time.perf_counter_ns() + ns
    while time.perf_counter_ns() < deadline:
        pass


def recv_line(sock: socket.socket, timeout: float = 5.0) -> str:
    """Read until newline."""
    sock.settimeout(timeout)
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(256)
        if not chunk:
            break
        buf += chunk
    sock.settimeout(None)
    return buf.decode(errors="replace").strip()


def calibration_cycle(sock: socket.socket) -> str:
    """Send 0xCA + 64×0x55, return response string."""
    # Enter CALIBRATE
    sock.sendall(bytes([0xCA]))
    time.sleep(0.01)

    # First 0x55 (trigger)
    sock.sendall(bytes([0x55]))

    # Remaining 63 with precise timing
    for _ in range(63):
        precise_sleep_ns(BYTE_TIME_NS)
        sock.sendall(bytes([0x55]))

    return recv_line(sock)


def main():
    print(f"[*] Connecting to {HOST}:{PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((HOST, PORT))
    print("[+] Connected\n")

    # ── Phase 1: Achieve LOCK ──────────────────────────────────────
    print("[*] Phase 1: Calibration")
    for attempt in range(1, 30):
        resp = calibration_cycle(sock)
        print(f"    Attempt {attempt:>2d}: {resp}")

        if "LOCKED" in resp:
            print("\n[+] LOCKED achieved!\n")
            break
        time.sleep(0.1)
    else:
        print("[!] Failed to LOCK after 29 attempts")
        sock.close()
        sys.exit(1)

    # ── Phase 2: Send MULT command ─────────────────────────────────
    print("[*] Phase 2: Multiplier")
    A = (7).to_bytes(64, "big")
    B = (6).to_bytes(64, "big")

    sock.sendall(bytes([0xAA]) + A + B)
    resp = recv_line(sock, timeout=10.0)
    print(f"    Response: {resp}")

    if resp.startswith("FLAG:"):
        flag = resp[5:]
        print(f"\n[+] FLAG CAPTURED: {resp}")

        # ── Phase 3: Verify against known fixed flag ──────────────
        if flag == FIXED_FLAG:
            print("    [*] MATCH — challenge solved!")
        else:
            print("    [!] MISMATCH — tamper fuse may be blown, reconnect")
    else:
        print(f"[!] Unexpected: {resp}")

    sock.close()
    print("\n[*] Done.")


if __name__ == "__main__":
    main()
```

### How to run:

```bash
# Start the server (pick one):
docker compose up --build            # Docker way
python device.py                     # Direct way

# Run the solver (in another terminal):
python solution.py 127.0.0.1 1337

# For best timing precision:
taskset -c 0 python solution.py 127.0.0.1 1337
```

---

## 8. Troubleshooting Common Issues

### "ERR: values are huge (±10000+ PPM)"

**Cause:** Nagle's algorithm is batching your sends.
**Fix:** Set `TCP_NODELAY`:
```python
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
```

### "ERR: values fluctuate wildly"

**Cause:** CPU scheduling jitter.
**Fix:**
- Run on a quiet machine
- Pin to a single CPU core: `taskset -c 0 python solution.py`
- Close other CPU-heavy applications
- If in Docker, ensure the container has dedicated CPU

### "Get LOCKED but flag doesn't match expected"

**Cause:** The tamper fuse was silently blown earlier in your session.

**Fix:** Disconnect and reconnect.  Only use valid opcodes (`0xCA`, `0x55`, `0xAA`).

### "TIMEOUT:SUPERCAP_DRAINED"

**Cause:** You took longer than 45 seconds after LOCKED to send the
multiplier command.

**Fix:** Send the `0xAA` + payload immediately after seeing `LOCKED`.

### "ERR:HSM_TAMPER_FUSE_BLOWN" appeared

**Cause:** You sent bytes that the HSM interpreted as a firmware dump or
debug probe.  The tamper fuse is now permanently blown for this session.

**Fix:** Disconnect immediately (`sock.close()`) and open a fresh TCP
connection.  Do NOT send any bytes other than `0xCA`, `0x55`, or `0xAA`.

### "Flags keep being wrong even though I get LOCKED"

**Cause:** The tamper fuse may have been silently blown earlier in the
session.  After the initial alert, the chip gives no further indication.

**Fix:** Disconnect and reconnect.  In your new session, ONLY use the
three valid opcodes.  Do not probe.

### "Connection resets / no response"

**Cause:** Invalid bytes reset the server to WAIT after 10 seconds.

**Fix:** Follow the protocol exactly:
- Only `0xCA` in WAIT state
- Only `0x55` bytes (exactly 64) in CALIBRATE
- Only `0xAA` + 128 bytes in LOCKED

---

## 9. Key Takeaways

1. **`time.sleep()` is useless for microsecond precision** — always use
   `time.perf_counter_ns()` spin loops for sub-millisecond timing.

2. **TCP_NODELAY matters** — Nagle's algorithm will destroy any attempt
   at byte-level timing over TCP.

3. **The flag is fixed** — once you achieve LOCK and send a valid MULT
   command, the flag is always `apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}`.
   The challenge gate is the precision timing, not the flag derivation math.

4. **Run locally for best results** — network latency and jitter
   between machines make precision timing over TCP extremely difficult.

5. **Do NOT probe the service** — The HSM tamper fuse is designed to
   punish firmware dump attempts.  It silently corrupts your session
   after a single warning.  Only use the documented protocol opcodes.
   If you trip it, disconnect and start fresh.

---

*End of solution guide.*




How to Solve Using solution.md
The solution has 3 phases:

Phase 1 — Achieve Baud Lock
Connect to the server (nc <host> 1337)
Send 0xCA to enter CALIBRATE mode
Send 64 bytes of 0x55 with timing matching 2,345,679 baud (4,263 ns per byte using a perf_counter_ns() busy-wait spin loop)
Read the ERR:±XXXXX PPM response
Repeat until you get 5 consecutive readings within ±1,000 PPM → server responds LOCKED
Critical: Set TCP_NODELAY, pin your process to a CPU core, run on the same machine as the server


Phase 2 — Get the Flag
Send 0xAA + 64 bytes for operand A + 64 bytes for operand B (e.g., A=7, B=6)
Server responds with FLAG:<64 hex chars>


Phase 3 — Verify the Flag
The flag is fixed: `apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}`
If your flag matches, the challenge is solved. If it doesn't match, the
tamper fuse was blown — disconnect and reconnect.