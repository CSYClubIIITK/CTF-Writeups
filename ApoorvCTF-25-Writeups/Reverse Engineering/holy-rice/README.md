## Description
A wise monk made a "totally unhackable" locker to guard his holy rice. Spoiler: it wasn't. The pigeon mafia is already on it — crack it first and claim the rice for yourself. 🐦🍚

- Author: hampter
- flag: apoorvctf{w41t#_th15_1s_1ll3g4l!}
- files: rice-cooker
- Category: Reverse Engineering

## Writeup

So we have a executable file to work with.

When you run it, it asks for a password, so somehow we either need to find the password or bypass this.

Running `file rice-cooker` we find it is `stripped` that means there will be no symbol table when debugging.

Opening file in a decompiler(i am using binaryninja you can you any like Ghidra, ida)

*main* 
```c
000014ff    int32_t main(int32_t argc, char** argv, char** envp)

0000150a        void* fsbase
0000150a        int64_t rax = *(fsbase + 0x28)
00001528        printf(format: "Enter password: ")
00001543        void buf
00001543        fgets(&buf, n: 0xc8, fp: stdin)
00001561        *(&buf + strcspn(&buf, u"\n…")) = 0
00001573        sub_1199(&buf)
00001582        sub_12cb(&buf)
00001591        sub_1418(&buf)
000015a0        sub_14a6(&buf)
000015c0        char const* const format
000015c0        
000015c0        if (strcmp(&buf, data_4048) != 0)
000015cb            format = &data_20e0
000015c0        else
000015c2            format = &data_20a0
000015c2        
000015da        printf(format)
000015e8        *(fsbase + 0x28)
000015e8        
000015f1        if (rax == *(fsbase + 0x28))
000015f9            return 0
000015f9        
000015f3        __stack_chk_fail()
000015f3        noreturn

```

we see that it takes input and puts it into `buf` then applies 4 functions `sub_1199`, `sub_12cb`, `sub_1418`, `sub_14a6` on that buf.

lets see them one by one

*sub_1199*
```c
00001199    int64_t sub_1199(char* arg1)

000011ab        void* fsbase
000011ab        int64_t rax = *(fsbase + 0x28)
000011cb        void var_78
000011cb        strcpy(&var_78, arg1)
000011d0        int32_t var_80 = 0
000011d0        
00001298        while (arg1[sx.q(var_80)] != 0)
000011dc            int32_t var_7c_1 = 0
000011dc            
00001279            while (sx.q(var_7c_1) u<= 0x26)
0000120d                if (arg1[sx.q(var_80)] == (*"0123456789abcdefghijklmnopqrstuv…")[sx.q(var_7c_1)])
00001266                    *(&var_78 + sx.q(var_80)) = (*"0123456789abcdefghijklmnopqrstuv…")[sx.q(var_7c_1 + 7) u% 0x27]
0000126a                    break
0000126a                
0000126c                var_7c_1 += 1
0000126c            
0000127f            var_80 += 1
0000127f        
000012af        strcpy(arg1, &var_78)
000012af        
000012c2        if (rax == *(fsbase + 0x28))
000012ca            return rax - *(fsbase + 0x28)
000012ca        
000012c4        __stack_chk_fail()
000012c4        noreturn
```
we see that here some kind of `substitution` is going on here.<br>
we find the position of every char of our input in `0123456789abcdefghijklmnopqrstuvwxyz_{}` and substitute with char at position `( pos+7 ) % length` then we copy the new string into our input string.

Onto the next function<br>

*sub_12cb*
```c
000012cb    int64_t sub_12cb(char* arg1)

000012dd        void* fsbase
000012dd        int64_t rax = *(fsbase + 0x28)
000012ec        int32_t var_e0 = 0
000012f6        int32_t var_dc = 0
000013d2        void var_d8
000013d2        
000013d2        while (arg1[sx.q(var_dc)] != 0)
00001319            int32_t rax_4 = var_e0
00001322            var_e0 = rax_4 + 1
0000132d            *(&var_d8 + sx.q(rax_4)) = arg1[sx.q(var_dc)]
0000132d            
0000135e            if (var_dc s% 3 == 0)
00001390                int32_t rax_21 = var_e0
00001399                var_e0 = rax_21 + 1
000013ac                *(&var_d8 + sx.q(rax_21)) = (*"!@#$%^&*()")[sx.q(var_dc) u% 0xa]
000013ac            
000013b3            var_dc += 1
000013b3        
000013e0        *(&var_d8 + sx.q(var_e0)) = 0
000013fc        strcpy(arg1, &var_d8)
000013fc        
0000140f        if (rax == *(fsbase + 0x28))
00001417            return rax - *(fsbase + 0x28)
00001417        
00001411        __stack_chk_fail()
00001411        noreturn
```
this function loops through our string, then for every index where `index % 3 == 0` it adds a special character from `!@#$%^&*()`, which character to solve is decided with special char at `index % 0xa`

Now onto next function.<br>
*sub_1418*
```c
00001418    int32_t sub_1418(char* arg1)

00001424        int32_t var_10 = 0
00001432        int32_t rax_1 = strlen(arg1)
0000149b        int32_t result
0000149b        
0000149b        while (true)
0000149b            result = (rax_1 + (rax_1 u>> 0x1f)) s>> 1
0000149b            
000014a0            if (var_10 s>= result)
000014a0                break
000014a0            
00001449            char rax_5 = arg1[sx.q(var_10)]
00001472            arg1[sx.q(var_10)] = arg1[sx.q(rax_1 - 1 - var_10)]
0000148b            arg1[sx.q(rax_1 - 1 - var_10)] = rax_5
0000148d            var_10 += 1
0000148d        
000014a5        return result

```
in this function we find length of our string and put in rax_1, `rax_1 = strlen(arg1)` and then does this `result = (rax_1 + (rax_1 u>> 0x1f)) s>> 1` which is just a fancy way of finding middle index of our string, hence this is equivalent to `strlen(arg1) / 2` <br>
then we loop from index 0 to middle and swapping char front and end so like `swap(arg[0], arg[n-1])`

Now onto the next function

*sub_14a6*
```c
000014a6    int64_t sub_14a6(void* arg1)

000014ae        int32_t var_c = 0
000014f4        char result
000014f4        
000014f4        while (true)
000014f4            result = *(arg1 + sx.q(var_c))
000014f4            
000014f9            if (result == 0)
000014f9                break
000014f9            
000014e1            *(arg1 + sx.q(var_c)) = (not.d(zx.d(*(arg1 + sx.q(var_c))) ^ 0xff)).b
000014e3            var_c += 1
000014e3        
000014fe        return result
```
this function is looping through our string, this take one byte at a time, then applies bitwise not then does xor with 0xFF then at the end joins all the bytes, combine and return.

Now after this 
```c
000015c0        if (strcmp(&buf, data_4048) != 0)
000015cb            format = &data_20e0
000015c0        else
000015c2            format = &data_20a0
```
our buf is compared with some `data_4048` checking value of this variable we get `6!!sbn*ass%84z@84c(8o_^4#_#8b0)5m_&j}y$vvw!h`

So summary of what happend so far.
1. takes input
2. substitution
3. add garbage
4. swap
5. not and xor
6. then check with hardcoded string

all of these are reversable funcitons hence we take the hardcoded string apply all functions in reverse then we get the password.

Here is my script
```py
subs = "0123456789abcdefghijklmnopqrstuvwxyz_{}"
shift = 7
garbage_chars = "!@#$%^&*()"
xor_key = 0xFF

def reverse_transform(text):
    transformed = [ord(c) for c in text]
    not_bytes = [b ^ xor_key for b in transformed]
    flag_bytes = [~b & 0xFF for b in not_bytes]
    flag = ''.join(chr(b) for b in flag_bytes)
    
    flag = flag[::-1]
    
    clean = ""
    for i in range(0, len(flag)):
        if (i - 1) % 4 != 0:
            clean += flag[i]
            
    result = ""
    for c in clean:
        if c in subs:
            idx = subs.index(c)
            result += subs[(idx - shift) % len(subs)]
        else:
            result += c
            
    return result

if __name__ == "__main__":
    encrypted = "6!!sbn*ass%84z@84c(8o_^4#_#8b0)5m_&j}y$vvw!h"
    flag = reverse_transform(encrypted)
    print(flag)
```

Running this we get `apoorvctf{w41t#_th15_1s_1ll3g4l!}`

Hope you learned something!