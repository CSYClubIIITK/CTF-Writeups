def str_xor(secret, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(secret))

def main():
    flag_enc_values = [
        0x63, 0x79, 0x62, 0x65, 0x72, 0x61, 0x72, 0x63, 0x7b,
        0x53, 0x63, 0x72, 0x31, 0x70, 0x74, 0x5f, 0x72, 0x41,
        0x6e, 0x5f, 0x53, 0x75, 0x63, 0x63, 0x65, 0x35, 0x35,
        0x66, 0x75, 0x6c, 0x6c, 0x79, 0x7d
    ]
    
    flag = ''.join(chr(value) for value in flag_enc_values)
    
    key = "windshine"
    
    encrypted_flag = str_xor(flag, key)
    
    print(encrypted_flag)
    
    decrypted_flag = str_xor(encrypted_flag, key)
    

if __name__ == "__main__":
    main()
