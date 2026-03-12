# The Leaky Router [Networking]

## Author: **orangcar**

## Challenge Description

In 2031, NeoCorp built an internal routing protocol called RTUN/1.0 to move messages across isolated nodes.
As an unprivileged user, you can only talk directly to Node 1. Node 3 is restricted and contains the flag.
The company believes Node 3 cannot be reached without trusted forwarding from inside the mesh.

## Solution

This challenge is a protocol-reversing + auth-bypass challenge.
The vulnerability is a hidden trust shortcut in the `FLAGS` byte:

`skip_auth = (flags == 0xFF)`

The intended story is: the engineer wanted to remove authentication overhead during testing, so they kept a special debug path where `FLAGS=0xFF` skips auth checks.
That testing shortcut remained in production logic and became the exploit path.

Below is the full solve process from recon to flag.

### RTUN Protocol Overview

Each packet on the wire is:

`HEADER (9 bytes) + PAYLOAD (variable) + CRC32 (4 bytes)`

Header format is big-endian `>BBIBH`:

1. `VERSION` (1 byte)
2. `FLAGS` (1 byte)
3. `TUNNEL_ID` (4 bytes)
4. `INNER_PROTO` (1 byte)
5. `PAYLOAD_LEN` (2 bytes)

**Minimum valid packet size:** `9 + 0 + 4 = 13 bytes`

CRC32 is computed over `header + payload`, then appended as 4 bytes.

**Validation order (important for reversing):**

1. VERSION check
2. Packet length floor/consistency check
3. CRC32 check
4. Protocol validity check
5. Tunnel routing + auth checks

### Packet Builder Function

Use this helper to generate valid RTUN packets:

```python
import struct
import zlib

HEADER_FMT = ">BBIBH"

def build_packet(version: int, flags: int, tunnel_id: int, inner_proto: int, payload: bytes) -> bytes:
    header = struct.pack(
        HEADER_FMT,
        version,       # VERSION
        flags,         # FLAGS
        tunnel_id,     # TUNNEL_ID
        inner_proto,   # INNER_PROTO
        len(payload),  # PAYLOAD_LEN
    )
    body = header + payload
    crc = struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    return body + crc
```

If CRC does not match, server responds with `RTUN/1.0 ERR_CHECKSUM`.

### Why `FLAGS=0xFF` Bypasses Authentication

Routing/auth logic is effectively:

1. Node 1: normal access
2. Node 2: requires authenticated/forwarded context
3. Node 3: only accepts trusted path (through Node 2 context)

But the implementation exposes:

`flags == 0xFF -> skip_auth = True`

So by sending `flags=0xFF`, attacker packets are treated as trusted test traffic and pass checks that should block direct access to Node 2/Node 3.

This is a common CTF pattern that mirrors real mistakes:

1. Temporary debug bypass for testing
2. No guardrail to disable in production
3. Critical path depends on a client-controlled field

### Step-by-Step Solving Approach

#### Step 1: Discover minimum RTUN packet length

1. Send all-zero blobs from length `1..32`.
2. Observe transition from length errors/incomplete behavior to version errors.
3. First consistent parser-level response appears at `13` bytes.
4. Infer minimum packet length is 13.

#### Step 2: Infer correct `VERSION`

1. Keep packet length fixed at 13.
2. Vary first byte (`VERSION`) from `0x00` upward.
3. Wrong version returns `ERR_VERSION`.
4. Correct version advances parser to checksum stage.
5. Recover `VERSION = 0x01`.

#### Step 3: Confirm checksum behavior

1. Build packet with valid-looking header and invalid CRC -> `ERR_CHECKSUM`.
2. Recompute CRC32 over `header+payload`.
3. Resend with corrected CRC -> parser advances.
4. Confirm checksum logic is standard CRC32.

#### Step 4: Enumerate `INNER_PROTO`

Probe protocol values with valid packets:

1. `0x01` -> `PLAINTEXT`
2. `0x02` -> `COMMAND`
3. `0x03` -> `FLAG_REQ`
4. `0x04` -> `ECHO`

Unknown values produce `ERR_PROTO`.

#### Step 5: Learn protocol payload rules

From responses:

1. `COMMAND` requires payload `STATUS`
2. `FLAG_REQ` requires payload `GIVE_FLAG`
3. `ECHO` requires non-empty data

Now we know exact shape needed for a flag request:

`INNER_PROTO=FLAG_REQ` + payload `GIVE_FLAG`

#### Step 6: Map tunnel behavior

Send `FLAG_REQ + GIVE_FLAG` across tunnel IDs:

1. Node 1 responds but does not return flag
2. Node 2 blocks with auth-related error unless bypass is active
3. Node 3 blocks with auth-related error unless bypass is active

Conclusion: final target is Node 3 with bypass enabled.

#### Step 7: Find the bypass `FLAGS` value

1. Fix fields:
   - `tunnel_id = 0x00000003`
   - `inner_proto = 0x03`
   - payload `GIVE_FLAG`
2. Sweep `flags` from `0x00` to `0xFF`.
3. Success appears at `flags=0xFF`.
4. Response: `RTUN/1.0 OK FLAG=...`

This confirms the engineer’s testing bypass is the intended vulnerability.

## Local Run Commands (Docker + Exploit)

From the `LEAKY_ROUTER` directory:

**Start server with Docker Compose:**

```bash
docker compose up --build -d
```

**Check container status/logs:**

```bash
docker compose ps
docker compose logs -f leaky_router_ctf
```

**Run exploit against local container:**

```bash
python3 exploit.py 127.0.0.1 3001
```

**Stop server:**

```bash
docker compose down
```
