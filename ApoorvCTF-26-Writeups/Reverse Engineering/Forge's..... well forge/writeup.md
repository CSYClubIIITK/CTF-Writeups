# Forge's..... well forge — Writeup

**Category:** Reverse Engineering / Bare-Metal Programming  
**Flag:** `APOORVCTF{Y0u_4ctually_brOught_Y0ur_owN_Firmw4re????!!!}`

---

## Initial Recon

We're given a single stripped 64-bit PIE ELF binary called `host`. Running it produces no output and exits with code 1.

```
$ file host
host: ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped

$ ./host
$ echo $?
1
```

`strings` gives us nothing useful — no error messages, no filenames, no banners. But the dynamic imports tell us a lot:

```
$ readelf -r host | grep JUMP_SLO
  EVP_EncryptUpdate     EVP_EncryptInit_ex    fork
  OPENSSL_cleanse       EVP_CIPHER_CTX_new    EVP_DigestFinal_ex
  EVP_DigestInit_ex     waitpid               ptrace
  time                  EVP_CIPHER_CTX_free   __stack_chk_fail
  EVP_MD_CTX_new        prctl                 RAND_bytes
  EVP_CIPHER_CTX_ctrl   EVP_aes_256_gcm       sigprocmask
  EVP_EncryptFinal_ex   _exit                 EVP_sha256
  mmap                  EVP_MD_CTX_free       EVP_DigestUpdate
```

Key observations:
- **`ptrace`** — anti-debug
- **`mmap`** — memory mapping
- **`fork` / `waitpid`** — process isolation (sandboxing?)
- **`prctl`** — likely seccomp setup
- **`sigprocmask`** — signal handling
- **`EVP_aes_256_gcm` / `EVP_Encrypt*`** — AES-256-GCM encryption
- **`EVP_sha256` / `EVP_Digest*`** — SHA-256 hashing (verification)
- **`OPENSSL_cleanse`** — secure memory wiping
- **`time`** — timestamp (probably key derivation)
- **Only encrypt functions, no decrypt** — huge hint: AES-GCM uses CTR mode internally, so encrypt ≡ decrypt

## Static Analysis

### Anti-Debug

```asm
call   ptrace@plt        ; ptrace(PTRACE_TRACEME)
cmp    rax,0xffffffffffffffff
je     die                ; if failed → exit
```

Followed by `sigprocmask` to block SIGCHLD (avoids ptrace-stop issues when the child process dies later). Patch out the ptrace conditional jump for debugging.

### Memory Mapping

Two fixed-address mappings:
- `0x20000000` — RWX, 4096 bytes (**CODE region** — firmware goes here)
- `0x40000000` — RW, 4096 bytes, **MAP_SHARED** (**MMIO region** — shared between parent and child)

The MAP_SHARED on MMIO is critical — it means the child process's writes are visible to the parent.

### GF(256) Matrix System

A ~64KB block in `.rodata` is a 256×256 GF(256) multiplication table, alongside a 56×56 matrix and a 56-element vector. At runtime, the host solves `M·F = V` over GF(256) via Gaussian elimination to recover a 56-byte flag plaintext. This plaintext only exists briefly before being encrypted and wiped.

This is a **red herring** for the solver — you never need to touch this math because the host encrypts the result and hands it to your firmware.

### Dual-Channel Architecture

The host doesn't just encrypt the flag — it encrypts **two channels** with the same AES key:

1. **Channel 0 (flag):** The actual flag (56 bytes)
2. **Channel 1 (challenge):** 56 random bytes, freshly generated each run

Both channels use the same AES-256-GCM key (derived from the timestamp) but different random nonces. The host pre-computes `SHA-256(challenge_plaintext)` and stores it in the parent's memory.

After the firmware decrypts both channels, the host verifies channel 1:
```
SHA-256(challenge_output) == stored_challenge_hash?
```

If this matches, the firmware proved it can actually perform AES-256-GCM decryption (not just replaying known data), and channel 0's output is written to stdout.

### MMIO Register Layout

```
Offset  Size  Field
0x000     4   current_timestamp (uint32 LE)
0x004    12   flag_nonce
0x010   128   flag_ciphertext (first 56 bytes matter)
0x090    16   flag_auth_tag
0x0A0    12   challenge_nonce
0x0AC   128   challenge_ciphertext (first 56 bytes matter)
0x12C    16   challenge_auth_tag
0x13C   128   flag_output          ← firmware writes decrypted flag here
0x1BC   128   challenge_output     ← firmware writes decrypted challenge here
```

### IIR Key Derivation

The 32-byte AES key is deterministically derived from the timestamp:

```
Input: x[0..3] = 4 LE bytes of unix timestamp
Output: k[0..31], initially all zeros

For i = 0..31:
    k[i] = (x[i % 4] >> 1) + x[(i+3) % 4] - (k[(i+31) % 32] >> 2)
```

The feedback term `k[(i+31) % 32] >> 2` makes this a sequential recurrence — each byte depends on the previous one.

### Fork + Seccomp Sandbox

This is the security architecture that prevents cheating:

1. **`fork()`** — the firmware runs in a child process
2. **`close(0, 1, 2)`** — the child's stdio is closed (no file descriptors)
3. **`prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, …)`** — a BPF filter is installed that **kills the process on any I/O syscall**

The seccomp whitelist only allows:
- Memory management: `brk`, `mmap`, `mprotect`, `munmap`, `mremap`
- Synchronization: `futex`
- Random: `getrandom`
- Signal: `rt_sigreturn`
- Exit: `exit_group`, `exit`

**Everything else is killed** — `write`, `read`, `open`, `socket`, `sendto`, etc. The firmware **cannot exfiltrate data** via syscalls. It can only compute and write to the shared MMIO page, then return.

After the child exits, the parent (which has full syscall access):
1. Checks the child exited cleanly (not killed by seccomp)
2. Reads `challenge_output` from the shared MMIO page
3. Computes `SHA-256(challenge_output)` and compares to the stored hash
4. If match → writes `flag_output` to stdout

### Obfuscated Filename

The payload filename is XOR-decoded at runtime. Each byte XORed with `0x5A` yields **`payload>bin`** (the `>` is deliberate — not a `.`).

## The Key Insight

AES-GCM internally uses CTR mode, which is just XOR with a keystream. **Encrypting the ciphertext with the same key and nonce produces the original plaintext.** We don't need to decrypt — we just call the encrypt functions again.

Since the host's OpenSSL PLT stubs are loaded in the process address space, and OpenSSL was already initialized by the parent before fork, we can call them directly from the firmware without triggering any I/O syscalls.

## Writing the Firmware

Our payload (437 bytes of x86-64 shellcode) must:

1. **Recover the PIE base** — the return address on the stack points to `base + 0x191b` (after `call rax`). Subtract to get the PIE base.

2. **Re-derive the AES key** — read 4 timestamp bytes from MMIO+0x00, run the IIR filter to produce 32 key bytes.

3. **Decrypt Channel 0 (flag):**
   - `EVP_CIPHER_CTX_new()` → create context
   - `EVP_aes_256_gcm()` → get cipher type
   - `EVP_EncryptInit_ex()` → set cipher, then set key + flag_nonce (MMIO+0x04)
   - `EVP_CIPHER_CTX_ctrl()` → set IV length to 12
   - `EVP_EncryptUpdate(ctx, MMIO+0x13C, …, MMIO+0x10, 56)` — flag "decryption"
   - `EVP_CIPHER_CTX_free()`

4. **Decrypt Channel 1 (challenge):** Same process but with:
   - Nonce from MMIO+0x0A0
   - Ciphertext from MMIO+0x0AC
   - Output to MMIO+0x1BC

5. **`ret`** — return cleanly so the parent can verify.

The full payload is in [`payload.asm`](payload.asm).

## Building & Running

```bash
# Assemble (note the literal '>' in the filename)
nasm -f bin payload.asm -o 'payload>bin'

# Run
./host
APOORVCTF{Y0u_4ctually_brOught_Y0ur_owN_Firmw4re????!!!}
```

## Why Shortcuts Don't Work

| Shortcut attempt | Why it fails |
|---|---|
| Extract flag from static data (GF256 solve) | You get the flag bytes, but can't exfiltrate — seccomp kills on `write()`, fds are closed |
| `syscall write(1, flag, 56)` in firmware | Seccomp BPF kills the process; fd 1 is closed anyway |
| Overwrite the challenge hash on the stack | It's in the *parent's* memory — fork gives the child a COW copy that can't affect the parent |
| Return known data to flag_output | Challenge verification fails — SHA-256(garbage) ≠ challenge_hash |
| Call `_exit(0)` without decrypting | Verification fails — challenge_output is all zeros |
| Solve only the GF(256) system | Still need to pass challenge verification, which requires decrypting a random per-run ciphertext with AES-256-GCM |

## Summary

| Step | What |
|------|------|
| 1 | Identify imports → AES-GCM + fork/seccomp sandbox pattern |
| 2 | Trace mmap calls → CODE (`0x20000000`) and shared MMIO (`0x40000000`) |
| 3 | Reverse the dual-channel MMIO struct layout from encrypt call arguments |
| 4 | Reverse the IIR key derivation loop |
| 5 | Decode XOR-obfuscated filename → `payload>bin` |
| 6 | Realize encrypt = decrypt in CTR mode |
| 7 | Write x86-64 shellcode that calls OpenSSL PLT functions via PIE base recovery |
| 8 | Decrypt **both channels** and write to correct MMIO output fields |
| 9 | Profit |
