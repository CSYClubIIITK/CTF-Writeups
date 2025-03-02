import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from random import randbytes

def main():
    key = randbytes(16)
    cipher = AES.new(key, AES.MODE_ECB)
    flag = b'apoorvctf{fake_flag_123}'

    print("Welcome to the ECB Oracle challenge!")
    print("Enter your input in hex format.")

    try:
        while True:
            print("Enter your input: ", end="", flush=True)
            userinput = sys.stdin.readline().strip()

            if not userinput:
                break

            try:
                userinput = bytes.fromhex(userinput)
                ciphertext = cipher.encrypt(pad(userinput + flag + userinput, 16))
                print("Ciphertext:", ciphertext.hex())

            except Exception as e:
                print(f"Error: {str(e)}")

    except KeyboardInterrupt:
        print("Server shutting down.")

if __name__ == "__main__":
    main()
