from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
import random

flag = b"apoorvctf{fake_flag}"

def secret(p):
    prime_bytes = p.to_bytes(64, byteorder='big')  
    keys = [bytes_to_long(prime_bytes[i:i+4]) for i in range(0, 64, 4)] 
    enc_p = []
    for key in keys:
        tp = []
        random.seed(key)
        indexes = [0, 1, 2, 227, 228, 229]
        random_arr = [random.getrandbits(32) for _ in range(624)] 
        for j in indexes:
            tp.append(random_arr[j])
        enc_p.append(tp) 
    return enc_p

def encrypt():
    p = getPrime(512)
    q = getPrime(512)
    n = p * q
    e = 65537
    c = pow(bytes_to_long(flag), e, n)
    trash = secret(p)  
    return n, c, trash  

def decrypt(n,p,c):
    q = n//p
    if p*q != n:
        print("Invalid n")
        return
    phi = (p-1)*(q-1)
    d = pow(65537,-1,phi)
    return long_to_bytes(pow(c,d,n))

n, c, trash = encrypt() 
print("n:", n)
print("c:", c)
print("trash:", trash)
#print("flag:", decrypt(n,p,c)) 


