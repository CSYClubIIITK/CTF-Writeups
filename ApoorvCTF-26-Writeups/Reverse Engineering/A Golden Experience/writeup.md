# A Golden Experience — Writeup

**Category:** Rev  
**Difficulty:** 4/10  
**Flag:** `apoorvctf{N0_M0R3_R3QU13M_1N_TH15_3XP3R13NC3}`

---

## Recon

We get a single stripped 64-bit ELF called `requiem`. Running it:

```
$ file requiem
requiem: ELF 64-bit LSB executable, x86-64, dynamically linked, stripped

$ ./requiem
loading flag
printing flag.....
RETURN TO ZERO!!!!!!!!
```

Says "printing flag....." but nothing actually shows up. Grepping strings turns up nothing useful either — just the messages themselves, no flag.

```
$ strings requiem | grep -i flag
loading flag
printing flag.....
```

So the flag is encoded or obfuscated somewhere in the binary. Time to throw it in a disassembler.

---

## Reversing

Binary is stripped, so we trace from `_start` through the Rust runtime shim into `main`. Three things stand out immediately:

**1. Encoded blob in `.rodata`** — 45 bytes of non-printable garbage:
```
3B 2A 35 35 28 2C 39 2E 3C 21 14 6A 05 17 6A 08
69 05 08 69 0B 0F 6B 69 17 05 6B 14 05 0E 12 6B
6F 05 69 02 0A 69 08 6B 69 14 19 69 27
```

**2. Single-byte XOR** with `0x5A` in a loop that processes the blob and pushes results into a `Vec<u8>`.

```asm
xor    reg, 0x5a
```

**3. `write_volatile` zeroing loop** right after — a bunch of `mov BYTE PTR [ptr], 0x0` with volatile semantics that wipes the decrypted buffer. And there's **no** `write` syscall or `println!` that ever touches the decrypted data. The flag literally never hits stdout.

So the trick is: the binary decrypts the flag onto the heap, immediately scrubs it with `write_volatile` (so the compiler can't optimize it away), and exits. There's nothing to patch — no print call to un-NOP. You either grab it from memory at runtime or decrypt it statically.

---

## Solving

Two paths here, both trivial once you spot the XOR.

### Static: just XOR it offline

Dump the 45 encrypted bytes from `.rodata`, XOR each with `0x5A`, done. Wrote a one-liner for this (see `solve.py`).

### Dynamic: GDB

Set a breakpoint after the XOR decryption loop but before the `write_volatile` wipe kicks in. The decrypted flag sits in a heap-allocated `Vec<u8>` — just read it out.

```
$ gdb ./requiem
(gdb) break *<addr_before_volatile_wipe>
(gdb) run
loading flag
printing flag.....
Breakpoint 1 hit

(gdb) x/s *(char**)($rsp + 0x8)
"apoorvctf{N0_M0R3_R3QU13M_1N_TH15_3XP3R13NC3}"
```

The `Vec<u8>` layout on the stack is `[ptr, len, cap]` — dereference the pointer and you're looking at the flag.

---

## Flag

```
apoorvctf{N0_M0R3_R3QU13M_1N_TH15_3XP3R13NC3}
```

Straightforward single-byte XOR with a volatile wipe gimmick. The only real "gotcha" is realizing there's no print to patch — you have to either freeze memory with a debugger or just do the XOR yourself.

*"What you have witnessed... is indeed the truth."* 
need to get the jojo reference somehow

