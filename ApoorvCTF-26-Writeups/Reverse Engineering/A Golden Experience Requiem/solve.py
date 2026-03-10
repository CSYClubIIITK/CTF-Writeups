#!/usr/bin/env python3
import sys

SHA256_IV = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]

def rotl8(v: int, by: int) -> int:
    v &= 0xFF
    return ((v << by) | (v >> (8 - by))) & 0xFF

def key1(i: int) -> int:
    return ((i * 7 + 63) & 0xFF) ^ rotl8(i, 3)

def key2(i: int) -> int:
    word = SHA256_IV[i & 7]
    shift = ((i >> 3) & 3) * 8
    return (word >> shift) & 0xFF

def full_key(i: int) -> int:
    return key1(i) ^ key2(i)

FLAG_PREFIX = b"apoorvctf{"
EVEN_ANCHOR = bytes([FLAG_PREFIX[i] ^ full_key(i) for i in range(0, 10, 2)])
ODD_ANCHOR = bytes([FLAG_PREFIX[i] ^ full_key(i) for i in range(1, 10, 2)])

def find_candidates(data: bytes, anchor: bytes, length: int) -> list:
    hits, start = [], 0
    while True:
        pos = data.find(anchor, start)
        if pos == -1:
            break
        if pos + length <= len(data):
            hits.append((pos, data[pos:pos + length]))
        start = pos + 1
    return hits

def interleave(even: bytes, odd: bytes) -> bytes:
    bc = bytearray(40)
    for k in range(20):
        bc[2 * k] = even[k]
        bc[2 * k + 1] = odd[k]
    return bytes(bc)

def decrypt_bytecode(bc: bytes) -> bytes:
    return bytes([(bc[i] ^ full_key(i)) & 0xFF for i in range(40)])

def is_valid_flag(raw: bytes) -> bool:
    try:
        s = raw.decode("utf-8")
        return (s.startswith("apoorvctf{") and s.endswith("}") and
                all(0x20 <= ord(c) < 0x7F for c in s))
    except:
        return False

def solve(binary_path: str) -> None:
    data = open(binary_path, "rb").read()
    print(f"[*] Binary: {binary_path} ({len(data):,} bytes)")
    print(f"[*] EVEN anchor: {EVEN_ANCHOR.hex()}")
    print(f"[*] ODD anchor:  {ODD_ANCHOR.hex()}")
    print()

    even_hits = find_candidates(data, EVEN_ANCHOR, 20)
    odd_hits = find_candidates(data, ODD_ANCHOR, 20)

    print(f"[*] BC_EVEN candidates: {len(even_hits)}")
    for off, blob in even_hits:
        print(f"    0x{off:08x} {blob.hex()}")
    print(f"[*] BC_ODD candidates:  {len(odd_hits)}")
    for off, blob in odd_hits:
        print(f"    0x{off:08x} {blob.hex()}")
    print()

    for eoff, even in even_hits:
        for ooff, odd in odd_hits:
            if eoff == ooff:
                continue
            flag = decrypt_bytecode(interleave(even, odd))
            if is_valid_flag(flag):
                print(f"[+] BC_EVEN @ 0x{eoff:08x}")
                print(f"[+] BC_ODD  @ 0x{ooff:08x}")
                print(f"[+] FLAG: {flag.decode()}")
                return

    print("[!] No valid flag found. Check key reversals and SHA256_IV.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary>")
        sys.exit(1)
    solve(sys.argv[1])
