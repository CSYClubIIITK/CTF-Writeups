# Golden Experience Requiem — Writeup

> "Your ability to live ends here." — But your ability to reverse engineer? That begins now.

**Challenge:** A Golden Experience Requiem  
**Category:** Reverse Engineering  
**Author:** shura356  
**Flag:** `apoorvctf{1_h0pe_5BR_i5_w33kly_rele4as3}`

## Overview

The binary crashes on startup and never prints the flag. You have to extract it statically from the binary. It's a Rust ELF with bunch of anti-analysis tricks (ptrace checks, timing gates, hypervisor detection), but the real game is understanding the crypto.

Ciphertext is split across two 20-byte arrays in `.rodata`, encrypted with two XOR keys derived from different sources. Red herrings everywhere: fake flags with JoJo jokes, unused AES crypto, SHA-256 constants that actually matter. Find the real ciphertext, reverse both keys, and you're done.

## Static Analysis Path

### Step 1: Find the Ciphertext

Open it in Ghidra and poke around `.rodata`. You'll hit several things:

- **`apoorvctf{wh4t_1f_k1ng_cr1ms0n_requ13m3d??}`** — Visible via `strings`. Perfectly formatted CTF flag. This one's fake—it's the joke setup, not the answer. Shows up quick and easy to trick you into submitting wrong.

- **`apoorvctf{y0u_g0t_k1ng_cr1ms0n3d_lmfao_}`** — This is DECOY_A. 40 bytes that decrypt to a valid flag if you use only the first key. First 8 bytes match the v1 challenge's BYTECODE, so pattern matching finds it first. The trap: it's missing half the key. You get duped into thinking you solved it.

- **More garbage:** DECOY_B, DECOY_C—encrypted with extra twists or just noise. Ignore them.

- **AES S-box** — Full 256-byte AES table. `findcrypt` will scream about it. There's even a `fake_aes_decrypt()` function. Completely unused for the real flag. Red herring that looks legit.

- **SHA-256 IVs** — 8 u32 constants sitting between the real ciphertext. Most people see SHA256 next to AES and assume it's part of the crypto. It is—but not how you think. These feed the second key, not the first.

- **BC_EVEN and BC_ODD** — The actual ciphertext, split and non-contiguous. 20 bytes each, separated by junk. If you search for a continuous 40-byte pattern, you won't find it. `BC[2k] = BC_EVEN[k]`, `BC[2k+1] = BC_ODD[k]`.

### Step 2: Reverse the Keys

The SIGSEGV handler processes the bytecode by XORing each byte with two keys. Decompile it and reverse both.

**Key 1:** MBA mess that simplifies to:
```
key1(i) = (i*7 + 63) XOR rotl8(i, 3)
```
Just arithmetic and rotation. The MBA obfuscation makes it look worse than it is.

**Key 2:** Pulls bytes from the SHA-256 IVs:
```
key2(i) = (SHA256_IV[i & 7] >> (8 * ((i >> 3) & 3))) & 0xFF
```
Pick one of 8 constants based on `i & 7`, shift to grab one of its 4 bytes based on `(i >> 3) & 3`. The constants look decorative—they're actually critical.

### Step 3: Known-Plaintext Attack

The flag format is fixed: `apoorvctf{...}`. That 10-char prefix anchors the first 5 bytes of BC_EVEN and first 5 bytes of BC_ODD.

Compute what those bytes look like encrypted:
```python
EVEN_ANCHOR = encrypt(b"a", key(0)) + encrypt(b"o", key(2)) + encrypt(b"r", key(4))
            + encrypt(b"v", key(6)) + encrypt(b"c", key(8))
ODD_ANCHOR  = encrypt(b"p", key(1)) + encrypt(b"o", key(3)) + encrypt(b"v", key(5))
            + encrypt(b"t", key(7)) + encrypt(b"f", key(9))
```

Search the binary for both patterns. Try every candidate pair, decrypt it, see if it's valid UTF-8 and looks like a flag. One of them will be right.

### Step 4: Decrypt

Interleave the two arrays:
```
BC[2k]     = BC_EVEN[k]
BC[2k + 1] = BC_ODD[k]
```

XOR each byte with both keys:
```
plaintext[i] = BC[i] XOR key1(i) XOR key2(i)
```

Check it's valid: starts with `apoorvctf{`, ends with `}`, valid UTF-8, printable ASCII. Done.

## The Traps

- **Fake flag via `strings`:** Just a joke sitting in `.rodata`. "what if King Crimson requiemed??" It's thematic flavor, not the real flag.

- **DECOY_A:** Looks like a real 40-byte encrypted flag (first 8 bytes match the v1 bytecode), decrypts to valid UTF-8 with only key1. Missing key2. Most people who find this think they won and stop. You get a plausible wrong answer.

- **DECOY_B and DECOY_C:** Extra garbage encrypted with twists. Just noise. Ignore.

- **AES S-box:** Full substitution table that `findcrypt` will detect. There's a whole `fake_aes_decrypt()` function that uses it on fake data. Wastes a lot of time if you follow it. Zero connection to the real flag.

- **SHA-256 IVs:** Sit between the real ciphertext arrays. Look decorative next to the AES box. They're not. They're the second key source. Miss them and you only get DECOY_A.

- **Split ciphertext:** Two 20-byte arrays instead of one 40-byte array. Pattern matching fails. Forces you to understand the architecture.
