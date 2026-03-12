# Dead Reckoning — CTF Writeup

**Category:** Reverse Engineering / Hardware Forensics  
**Difficulty:** Medium  
**Files:** `controller_fw.bin`

---

## Challenge Description

> A damaged embedded CNC controller was discovered at an abandoned research facility. The machine was mid-job when the power got cut. The engineers said the machine was engraving something important before it died. Can you recover what it was making and find the flag in the process?
>
> The flag contains the characters `f'` to identify it when you see it.
>
> The only file the team was able to recover from the CNC machine is the binary file last loaded onto the embedded controller. Good luck.

---

## Overview

This challenge involves recovering a GCode toolpath from a raw embedded firmware binary. The binary is not an executable — it is a flat memory image dumped from a microcontroller's flash storage. The solve path goes through four stages: binary reconnaissance, config struct analysis, XOR decoding of job segments, and GCode visualisation.

---

## Stage 1 — Binary Reconnaissance

The first tool to reach for on any unknown binary is `strings`. It extracts all sequences of printable characters four bytes or longer, and on firmware binaries it is usually extremely revealing.

```bash
strings controller_fw.bin
```

Output (relevant lines):

```
AXIOM-CNC fw v2.3.1
AXIOM-EMB-32 (c) 2021 Axiom Precision Ltd
job_buffer_load: segment %d of %d
WARNING: CRC mismatch on segment header
FAULT: watchdog timeout during job_exec at flash+0x00001000
spindle_on: PWM duty %d%%
axis_limit_exceeded: halting
SAFE MODE ACTIVE
JOB BUFFER FRAGMENTED
job_buffer: packet format [4B:length][1B:seg_id][NB:data] x4 segments
[AXIOM DEBUG] config struct OK (sizeof=34 bytes, magic=0xAA104D43): magic=0x%08X baud=%d x_max=%.1f y_max=%.1f z_max=%.1f feed_max=%d spindle_max=%d cal_reserved=%s
cal_reserved (0x0C18): DO NOT MODIFY
JBUFHDR5SEG4
AXIOM_END
```

Several things stand out immediately.

**The firmware is for an industrial CNC controller.** Version strings, axis limit fields, spindle and feed rate references — this is a real machine controller binary.

**The watchdog fault at `flash+0x00001000` is a crash log.** A watchdog timer on embedded systems resets the chip if the firmware stops responding — consistent with the "power cut mid-job" narrative. More importantly, this tells us the machine died while executing job code at address `0x1000`. That address is a direct pointer to the job data region in flash.

> **Note:** The `WARNING: CRC mismatch` line is a red herring. Inspecting the binary in a hex editor reveals no structural corruption. The file is intact — confirmed by the clean `AXIOM_END` footer at the end of the binary.

**The packet format descriptor is the most valuable string:**
```
job_buffer: packet format [4B:length][1B:seg_id][NB:data] x4 segments
```
This tells us the complete structure of each job data packet — a 4-byte little-endian length, a 1-byte segment ID, then the payload — and that there are 4 of them.

**The config debug string gives us a complete struct map:**
```
[AXIOM DEBUG] config struct OK (sizeof=34 bytes, magic=0xAA104D43): magic=0x%08X baud=%d x_max=%.1f y_max=%.1f z_max=%.1f feed_max=%d spindle_max=%d cal_reserved=%s
```
This is a C-style `printf` format string used for debug logging. It names every field in the config struct in order, along with the struct's total size (34 bytes) and its magic number (`0xAA104D43`). The last field — `cal_reserved` — is a `%s` (string type), flagged by the next line as something we should not touch.

---

## Stage 2 — Config Struct Analysis

With the magic number `0xAA104D43` in hand, we search the hex dump for its little-endian byte representation: `43 4D 10 AA`.

```bash
hexdump -C controller_fw.bin >> hex_dump.txt
grep -n "43 4d 10 aa" hex_dump.txt
```

Or search directly in a hex editor. The bytes appear at offset `0x0C00` — confirming the config struct starts there.

```
00000c00  43 4d 10 aa 00 c2 01 00  00 00 48 43 00 00 48 43  |CM........HC..HC|
00000c10  00 00 48 42 90 01 c0 5d  f1 4c 3b a7 2e 91 c4 08  |..HB...].L;.....|
00000c20  04 de 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
```

Mapping the format string fields onto the bytes:

| Offset | Bytes | Type | Value | Field |
|--------|-------|------|-------|-------|
| `0x0C00` | `43 4D 10 AA` | uint32 | `0xAA104D43` | magic |
| `0x0C04` | `00 C2 01 00` | uint32 LE | `115200` | baud rate |
| `0x0C08` | `00 00 48 43` | float32 | `200.0` | x_max (mm) |
| `0x0C0C` | `00 00 48 43` | float32 | `200.0` | y_max (mm) |
| `0x0C10` | `00 00 48 42` | float32 | `50.0` | z_max (mm) |
| `0x0C14` | `90 01` | uint16 | `400` | feed_max |
| `0x0C16` | `C0 5D` | uint16 | `24000` | spindle_max |
| **`0x0C18`** | **`f1 4c 3b a7 2e 91 c4 08`** | **string[8]** | — | **cal_reserved** |
| `0x0C20` | `04` | uint8 | `4` | segment_count |
| `0x0C21` | `DE` | uint8 | checksum | — |

The warning line told us `cal_reserved` lives at `0x0C18`. We go there and read 8 bytes:

```
f1 4c 3b a7 2e 91 c4 08
```

These bytes are non-printable — which is why they never appeared in the `strings` output. This is the XOR key.

---

## Stage 3 — Decoding the Job Segments

### Finding and Parsing the Job Buffer

We know from the watchdog fault that job data lives at `0x1000`. Jumping there in the hex dump:

```
00001000  4a 42 55 46 48 44 52 35  53 45 47 34 92 0f 00 00  |JBUFHDR5SEG4....|
```

Three readable ASCII tokens sit at the start of this region:

- `JBUF` — identifies this as the job buffer region
- `HDR5` — each packet header is 5 bytes (4-byte length + 1-byte segment ID)
- `SEG4` — 4 segments total

This matches `JBUFHDR5SEG4` from the `strings` output. The actual packet data begins at byte 12, immediately after these tokens.

The structure the packet format descriptor told us:

```
[4 bytes LE: data length] [1 byte: segment ID] [N bytes: XOR-encoded GCode]
```

Reading the first packet starting at offset `0x100C`:
- Bytes `92 0F 00 00` → little-endian `0x0F92` → **3986** bytes of data
- Byte `03` → segment ID **3**
- Next 3986 bytes → XOR-encoded GCode

The pattern repeats for all four packets. The segment IDs are shuffled — the binary stores them as `3, 0, 2, 1`. We need to sort by ID to recover the correct execution order.

### The XOR Decoding

XOR encoding works by applying a repeating key across every byte of the data:

```
encoded_byte = original_byte XOR key[position % key_length]
```

Because XOR is its own inverse, decoding is identical:

```
original_byte = encoded_byte XOR key[position % key_length]
```

### Solve Script

```python
import struct

# XOR key recovered from cal_reserved field at 0x0C18
KEY = b'\xF1\x4C\x3B\xA7\x2E\x91\xC4\x08'

with open('controller_fw.bin', 'rb') as f:
    f.seek(0x1000)
    data = f.read()

# verify JBUF header tokens
assert data[0:4]  == b'JBUF'
assert data[4:8]  == b'HDR5'
assert data[8:12] == b'SEG4'

# parse packets starting after the 12-byte header
offset = 12
segments = {}

for _ in range(4):
    length  = struct.unpack_from('<I', data, offset)[0]
    seg_id  = data[offset + 4]
    encoded = data[offset + 5 : offset + 5 + length]

    decoded = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(encoded))

    segments[seg_id] = decoded
    offset += 5 + length

# sort by ID to recover correct execution order (0,1,2,3)
gcode = b''.join(segments[i] for i in sorted(segments))
print(gcode.decode())
```

Running this produces clean, readable GCode across all four segments. The last segment contains a notable comment:

```
(seg:4/4)
(continue: AXIOM-DEBUG port 4444)
```

This is the pivot point to the next stage of the challenge.

---

## Stage 4 — Visualising the GCode

Save the decoded output to a `.ngc` file:

```bash
python3 solve.py > recovered.ngc
```

Load `recovered.ngc` into any GCode visualiser — [NCViewer](https://ncviewer.com), [CAMotics](https://camotics.org), or similar open-source tools. The rendered toolpath reveals the flag engraved as text.

The flag contains the identifier `f'` as noted in the challenge description.

---

## Summary

| Stage | What we found | How |
|-------|--------------|-----|
| Recon | Crash address `0x1000`, packet format, config magic, key address | `strings` |
| Config | XOR key `f1 4c 3b a7 2e 91 c4 08` at `0x0C18` | hexdump + struct mapping |
| Decode | 4 XOR-encoded GCode segments in shuffled order | Python solve script |
| Visualise | Flag text rendered as a CNC toolpath | GCode visualiser |

---

## Key Takeaways

- `strings` on firmware binaries is disproportionately powerful — developers leave debug format strings that effectively document the binary's own structure
- Magic numbers in binary structs are searchable landmarks — find the magic, find the struct
- XOR with a repeating key is common obfuscation in embedded systems due to its simplicity and low computational cost
- Length-prefixed binary formats are self-describing — you never need to know the total size upfront, the data tells you how much to read at each step
