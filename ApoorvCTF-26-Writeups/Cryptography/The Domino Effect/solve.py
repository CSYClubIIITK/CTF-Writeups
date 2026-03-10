#!/usr/bin/env python3

import json
import math
import sys
import scipy.special
import scipy.stats
import socket
import time
from functools import reduce
from operator import xor

HOST = "chals2.apoorvctf.xyz"
PORT = 13337

HEX_CHARS = b'0123456789abcdef'
LOG_TRUE = math.log(0.55 / 0.45)
LOG_FALSE = math.log(0.45 / 0.55)

BASELINE_ROUNDS = 5
CONFIDENCE_THRESHOLD = 0.93
AVG_QUERIES_PER_BYTE = 312

THROTTLE_BASELINE = 0.15
THROTTLE_INFO = 0.08

def Xor(*args):
    return bytes(reduce(xor, t) for t in zip(*args))

class Netcat:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.recv_until(b'\n')

    def recv_until(self, delimiter):
        out = b''
        while not out.endswith(delimiter):
            chunk = self.socket.recv(1)
            if not chunk:
                break
            out += chunk
        return out

    def send_json(self, data):
        self.socket.sendall(json.dumps(data).encode() + b'\n')
        resp = self.recv_until(b'\n')
        return json.loads(resp.decode())

    def close(self):
        self.socket.close()

def attempt_solve():
    try:
        nc = Netcat(HOST, PORT)
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        time.sleep(1)
        return None

    def interface(data):
        return nc.send_json(data)

    try:
        resp = interface({"option": "encrypt"})
        if "ct" not in resp:
            return None
        data_interface = bytes.fromhex(resp["ct"])
    except:
        return None

    nb_request = 0
    iv = data_interface[:16]
    cipher_message = data_interface[16:]
    plaintext = b""
    alphabet = HEX_CHARS

    print(f"[*] Starting attack... (Budget: {AVG_QUERIES_PER_BYTE} queries/byte)")

    for index_bloc in range(0, len(cipher_message), 16):
        found = b""

        for i in range(1, 17):
            current_byte_global_index = (index_bloc) + (i - 1)
            budget_ceiling = (current_byte_global_index + 1) * AVG_QUERIES_PER_BYTE

            candidates = []
            for k in range(256):
                byte_bruteforce = bytes([k]).hex()
                prev_block_slice = (iv + cipher_message)[index_bloc:index_bloc+16]
                prev_byte = prev_block_slice[16-i]

                if Xor(bytes.fromhex(byte_bruteforce), bytes([i]), bytes([prev_byte])) in alphabet:
                    cipher = bytes([0]*(16-i)).hex() + byte_bruteforce + found.hex()
                    cipher += cipher_message[index_bloc:index_bloc+16].hex()

                    candidates.append({
                        "byte": byte_bruteforce,
                        "cipher": cipher,
                        "log_ratio": 0,
                        "proba": 1.0 / 16
                    })

            for _ in range(BASELINE_ROUNDS):
                for cand in candidates:
                    res = interface({"option": "unpad", "ct": cand["cipher"]})["result"]
                    nb_request += 1
                    if res:
                        cand["log_ratio"] += LOG_TRUE
                    else:
                        cand["log_ratio"] += LOG_FALSE
                    time.sleep(THROTTLE_BASELINE)

            loop_count = 0
            while True:
                log_ratios = [x["log_ratio"] for x in candidates]
                softmax_ = scipy.special.softmax(log_ratios)
                for k in range(len(candidates)):
                    candidates[k]["proba"] = softmax_[k]

                candidates.sort(key=lambda x: x["proba"], reverse=True)
                leader = candidates[0]

                if leader["proba"] > CONFIDENCE_THRESHOLD:
                    break

                if nb_request > budget_ceiling:
                    break

                targets = [candidates[0]]
                if loop_count % 3 == 0 and len(candidates) > 1:
                    targets.append(candidates[1])

                for t in targets:
                    res = interface({"option": "unpad", "ct": t["cipher"]})["result"]
                    nb_request += 1
                    if res:
                        t["log_ratio"] += LOG_TRUE
                    else:
                        t["log_ratio"] += LOG_FALSE
                    time.sleep(THROTTLE_INFO)

                loop_count += 1

                if nb_request > 9900:
                    break

            if nb_request >= 10000:
                print("\n[-] Query limit exceeded.")
                nc.close()
                return None

            winner = candidates[0]["byte"]

            if i != 16:
                found = Xor(bytes.fromhex(winner) + found, bytes([i] * i), bytes([i+1] * i))
            else:
                found = bytes.fromhex(winner) + found

            sys.stdout.write(f"\rByte {current_byte_global_index+1}/32 | Queries: {nb_request} | Budget: {budget_ceiling} | Conf: {leader['proba']:.5f}")
            sys.stdout.flush()

        output_decryption = Xor(found, bytes([0x10] * 16))
        if index_bloc == 0:
            plaintext += Xor(output_decryption, iv)
        else:
            plaintext += Xor(output_decryption, cipher_message[index_bloc-16:index_bloc])

        print()

    try:
        decoded_pt = plaintext.decode()
        print(f"[+] Plaintext: {decoded_pt}")

        check_resp = interface({"option": "check", "message": decoded_pt})
        if "flag" in check_resp:
            nc.close()
            return check_resp["flag"]
        else:
            print("[-] Incorrect.")
            nc.close()
            return None

    except Exception as e:
        print(f"[-] Error: {e}")
        nc.close()
        return None

def main():
    attempt = 1
    while True:
        print(f"\n=== Attempt {attempt} ===")
        flag = attempt_solve()

        if flag:
            print("\n" + "="*50)
            print(f"Flag: {flag}")
            print("="*50)
            break
        else:
            print("[!] Failed. Retrying...")
            attempt += 1

if __name__ == "__main__":
    main()
