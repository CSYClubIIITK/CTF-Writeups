#!/usr/bin/env python3
import json
import math
import socket
import sys

from Crypto.Util.Padding import unpad

BLOCK_SIZE = 16
DEBUG = True

class Conn:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.buf = b''

    def readline(self):
        while b'\n' not in self.buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise ConnectionError("rip")
            self.buf += chunk
        line, self.buf = self.buf.split(b'\n', 1)
        return line.decode()

    def send_json(self, obj):
        msg = json.dumps(obj).encode() + b'\n'
        if DEBUG:
            print(f">> {obj}", file=sys.stderr)
        self.s.sendall(msg)

    def query(self, obj):
        self.send_json(obj)
        resp = json.loads(self.readline())
        if DEBUG:
            print(f"<< {resp}", file=sys.stderr)
        return resp


def leak_params(conn, a):
    resp = conn.query({"option": "math_test", "data": 0})
    b = resp["result"]
    print(f"[*] B = {b}")

    big_xs = [2**40 + 37, 2**40 + 12345, 2**41 + 999]
    multiples = []
    for x in big_xs:
        resp = conn.query({"option": "math_test", "data": x})
        r = resp["result"]
        multiples.append(a * x + b - r)

    p = multiples[0]
    for m in multiples[1:]:
        p = math.gcd(p, m)

    for f in range(2, 10000):
        while p % f == 0 and p // f >= (1 << 31):
            p //= f

    x_test = 2**39 + 7
    resp = conn.query({"option": "math_test", "data": x_test})
    assert (a * x_test + b) % p == resp["result"]
    print(f"[*] P = {p}")
    return b, p

def build_gated_ct(mod_prev, target, s_exp, p, shift_inv):
    fixed = mod_prev + target
    fixed_int = int.from_bytes(fixed, 'big')
    adj_int = ((s_exp - fixed_int) * shift_inv) % p
    adj = adj_int.to_bytes(16, 'big')
    return adj + fixed

def oracle(conn, mod_prev, target, a, b, p, s_cur, shift_inv):
    s_nxt = (a * s_cur + b) % p
    ct = build_gated_ct(mod_prev, target, s_nxt, p, shift_inv)
    
    temp = DEBUG
    globals()['DEBUG'] = False
    resp = conn.query({"option": "decrypt", "ct": ct.hex()})
    globals()['DEBUG'] = temp
    
    if "error" in resp:
        return None, s_cur
    
    is_ok = resp.get("oracle") == "padding_ok"
    return is_ok, s_nxt

def padding_oracle(conn, flag_ct, a, b, p, s_0):
    iv = flag_ct[:BLOCK_SIZE]
    ct = flag_ct[BLOCK_SIZE:]
    
    blocks = [ct[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE] for i in range(len(ct)//BLOCK_SIZE)]
    prevs = [iv] + blocks[:-1]
    
    shift_inv = pow(pow(2, 256, p), -1, p)
    
    plaintext = b''
    s = s_0
    queries = 0
    
    for blk_idx, (target, prev) in enumerate(zip(blocks, prevs)):
        print(f"[*] Block {blk_idx + 1}/{len(blocks)}")
        inter = [0] * BLOCK_SIZE
        
        for pos in range(BLOCK_SIZE - 1, -1, -1):
            pad = BLOCK_SIZE - pos
            
            for guess in range(256):
                mod = bytearray(BLOCK_SIZE)
                mod[pos] = guess
                for j in range(pos + 1, BLOCK_SIZE):
                    mod[j] = inter[j] ^ pad
                
                ok, s = oracle(conn, bytes(mod), target, a, b, p, s, shift_inv)
                queries += 1
                
                if ok is None:
                    continue
                if not ok:
                    continue
                
                if pad == 1:
                    mod_v = bytearray(mod)
                    mod_v[0] ^= 0x01
                    ok_v, s = oracle(conn, bytes(mod_v), target, a, b, p, s, shift_inv)
                    queries += 1
                    if not ok_v:
                        continue
                
                inter[pos] = guess ^ pad
                break
        
        pt = bytes(inter[j] ^ prev[j] for j in range(BLOCK_SIZE))
        plaintext += pt
        print(f"    queries: {queries}")
    
    return plaintext, queries

def main():    
    host = 'challs.apoorvctf.xyz'
    port = 13424
    
    conn = Conn(host, port)
    hs = json.loads(conn.readline())
    
    a = hs["lcg_params"]["A"]
    s_0 = hs["lcg_params"]["S_0"]
    flag_ct = bytes.fromhex(hs["flag_ct"])
    
    print(f"[*] A={a}, S_0={s_0}")
    print(f"[*] {len(flag_ct)} bytes ciphertext")
    
    b, p = leak_params(conn, a)
    
    raw, queries = padding_oracle(conn, flag_ct, a, b, p, s_0)
    conn.close()
    
    flag = unpad(raw, BLOCK_SIZE).decode()
    print(f"\n[+] Queries: {queries}")
    print(f"[+] Flag: {flag}")

if __name__ == "__main__":
    main()
