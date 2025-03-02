import hashlib

def check_hex_data(hex1, hex2, start_string):
    if hex1 == hex2:
        return "Error: Even a Saiyan warrior knows that true strength lies in difference! The two inputs must not be identical."

    try:
        data1 = bytes.fromhex(hex1)
        data2 = bytes.fromhex(hex2)
    except ValueError:
        return "Error: Looks like you misfired a Ki blast! Invalid hex input detected."

    start_bytes = start_string.encode()

    if not (data1.startswith(start_bytes) and data2.startswith(start_bytes)):
        return "Error: These aren't true warriors! Both inputs must start with the legendary sign of 'GOKU' to proceed."

    def md5_hash(data):
        hasher = hashlib.md5()
        hasher.update(data)
        return hasher.hexdigest()

    hash1 = md5_hash(data1)
    hash2 = md5_hash(data2)

    if hash1 != hash2:
        return "Error: These warriors are impostors! They wear the same armor but their Ki signatures (MD5 hashes) don't match."

    try:
        with open("flag.txt", "r") as flag_file:
            flag = flag_file.read().strip()
        return f"🔥 You have found the real Goku! Your flag is: {flag}"
    except FileNotFoundError:
        return "Error: The Dragon Balls couldn't summon the flag! 'flag.txt' is missing."

if __name__ == "__main__":
    start_string = "GOKU"
    hex1 = input("Enter first hex data: ")
    hex2 = input("Enter second hex data: ")
    print(check_hex_data(hex1, hex2, start_string))
