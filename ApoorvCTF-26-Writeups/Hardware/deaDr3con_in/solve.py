#!/usr/bin/env python3
"""
solve.py  —  Recovers the GCode from controller_fw.bin

How to run:
    python3 solve.py                  # prints GCode to terminal
    python3 solve.py > recovered.ngc  # saves to file for rendering
"""

import struct

# ── Step 1: find the XOR key
#
#    strings output reveals:
#      [AXIOM DEBUG] config struct OK (sizeof=34 bytes, magic=0xAA104D43):
#      magic=0x%08X baud=%d x_max=%.1f y_max=%.1f z_max=%.1f
#      feed_max=%d spindle_max=%d cal_reserved=%s
#
#      cal_reserved (0x0C18): DO NOT MODIFY
#
#    Search hex dump for magic bytes 43 4D 10 AA (0xAA104D43 little-endian)
#    → config struct confirmed at 0x0C00
#    Warning gives exact address → go to 0x0C18, read 8 bytes → XOR key
#
KEY = b'\xF1\x4C\x3B\xA7\x2E\x91\xC4\x08'

# ── Step 2: locate and understand the jobdata region
#
#    strings output reveals:
#      FAULT: watchdog timeout during job_exec at flash+0x00001000
#      job_buffer: packet format [4B:length][1B:seg_id][NB:data] x4 segments
#
#    Hex dump at 0x1000 shows three readable ASCII tokens:
#      JBUF  → this is the job buffer region
#      HDR5  → each packet header is 5 bytes (4 length + 1 seg_id)
#      SEG4  → 4 segments total
#
#    Packets begin immediately after the 12-byte header at offset 0x100C
#
with open('controller_fw.bin', 'rb') as f:
    f.seek(0x1000)
    data = f.read()

# verify the three ASCII tokens
assert data[0:4]  == b'JBUF', "JBUF magic not found"
assert data[4:8]  == b'HDR5', "HDR5 token not found"
assert data[8:12] == b'SEG4', "SEG4 token not found"

# ── Step 3: parse segment packets starting after the 12-byte header
#
#    Each packet: [4 bytes LE length][1 byte seg_id][N bytes XOR-encoded GCode]
#
offset = 12   # skip past JBUF + HDR5 + SEG4
segments = {}

for _ in range(4):
    length  = struct.unpack_from('<I', data, offset)[0]  # 4-byte little-endian length
    seg_id  = data[offset + 4]                           # 1-byte segment ID
    encoded = data[offset + 5 : offset + 5 + length]    # encoded GCode bytes

    # XOR decode — cycle the 8-byte key across every byte
    decoded = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(encoded))

    segments[seg_id] = decoded
    offset += 5 + length

# ── Step 4: sort by segment ID → correct playback order (0,1,2,3)
gcode = b''.join(segments[i] for i in sorted(segments))
print(gcode.decode())
