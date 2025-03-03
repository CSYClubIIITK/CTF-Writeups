import socket
import threading
import os
import time
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from random import randbytes

def client_timer(client_socket, addr):
    time.sleep(600)  # 10 minutes
    try:
        client_socket.send(b"Time is up for your session. Goodbye!\n")
        client_socket.close()
        print(f"Timeout for client {addr}")
    except:
        pass  # Socket might already be closed

# Use threading to handle multiple clients
def handle_client(client_socket, addr):
    print(f"Connection established with {addr}")
    
    # Start timer for this client only
    timer_thread = threading.Thread(target=client_timer, args=(client_socket, addr))
    timer_thread.daemon = True
    timer_thread.start()
    
    try:
        client_socket.send(b"Welcome to the ECB Oracle challenge!\n")
        client_socket.send(b"Enter your input in hex format.\n")
        
        key = randbytes(16)
        cipher = AES.new(key, AES.MODE_ECB)
        flag = b'apoorvctf{3cb_345y_crypt0_br34k}'
        
        while True:
            client_socket.send(b"Enter your input: ")
            userinput = client_socket.recv(1024).strip()
            
            if not userinput:
                break
                
            try:
                userinput = bytes.fromhex(userinput.decode())
                
                ciphertext = cipher.encrypt(pad(userinput + flag + userinput, 16))
                
                client_socket.send(b"Ciphertext: " + ciphertext.hex().encode() + b"\n")
                
            except Exception as e:
                client_socket.send(f"Error: {str(e)}\n".encode())
                
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Connection closed with {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind(('0.0.0.0', 9999))
    server.listen(100)
    print("Server is listening on port 9999")
    print("Server will run until manually shut down (Ctrl+C)")
    
    try:
        while True:
            client, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client, addr))
            client_handler.daemon = True
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down due to keyboard interrupt")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Server continuing to run...")
        main()
    finally:
        try:
            server.close()
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Attempting to restart server...")
        time.sleep(5)
        os.execv(sys.executable, ['python'] + sys.argv)  