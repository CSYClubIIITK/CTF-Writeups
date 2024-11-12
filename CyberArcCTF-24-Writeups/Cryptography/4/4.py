def encrypt(message):
    n = 4
    txt3gram = [message[i:i+n] for i in range(0, len(message), n)]
    encode_lst = []
    for chunk in txt3gram:
        if len(chunk) == 4: 
            encode_lst.append(chunk[1] + chunk[2] + chunk[0] + chunk[3])
        else:
            encode_lst.append(chunk)

    return ''.join(encode_lst)

def decrypt(encrypted_message):
    n = 4
    txt3gram = [encrypted_message[i:i+n] for i in range(0, len(encrypted_message), n)]
    decode_lst = []

    for chunk in txt3gram:
        if len(chunk) == 4:  
            decode_lst.append(chunk[2] + chunk[0] + chunk[1] + chunk[3])
        else:
            decode_lst.append(chunk)

    return ''.join(decode_lst)

def main():
    message = "Remember_to_clean_up_any_loose_ends._Delete_any_sensitive_messages_after_reading._We_cant_afford_any_slip-ups._Trust_no_one" 
    #  encrypted_message = encrypt(message)
    decrypted_message = decrypt("emRebemrto__leca_unpan_ylo_oe_sedsn.De_ltee_nya_ensstiiv_meesasgs_eatefrre_aindg_W.eca_n_atforfdan_ysl_i-upp._sTusrtno__one")
    #  print("Encrypted Message:", encrypted_message)
    print("decrypted Message:", decrypted_message)

if __name__ == '__main__':
    main()
