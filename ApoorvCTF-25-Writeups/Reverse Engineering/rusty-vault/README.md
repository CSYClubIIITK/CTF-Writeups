## Description
In the heart of an abandoned shrine, there’s an old, rusted vault said to guard an unspeakable secret. Many have tried to unlock it, but the door’s demands are strange and no key seems to fit.

- Author: hampter
- Flag: apoorvctf{P4tch_1t_L1k3_1t's_H0t1}
- Files: vault
- Category: Reverse Engineering

## Writeup

So we are given a executable file, running it asks for a secret phrase, giving something random says *Stage 1 failed!!"*

Run `file vault` to find that this is not stripped hence we can see symbol table while debugging.

Next i opened the program in a decompiler called binaryninja(you can use decompiler of you choice like Ghidra, ida)

Finding the main funciton 
*main*
```rs
0000c9e0    int32_t main(int32_t argc, char** argv, char** envp)

0000c9e0        int64_t rax
0000c9e0        int64_t var_8 = rax
0000c9f6        return std::rt::lang_start::hc2969f868802be45(vault::main::h24beb508db3a64db, sx.q(argc), argv, 0)
```
This just calls `vault::main::h24beb508db3a64db`

Going there a long chunk of code is found.
Looking at code we can see it takes user input then trims it then calculates length of the input in `rax_7` which i renamed to `input_len`
```rs
0000c34a        rax_5, rdx_3 = core::str::_$LT$impl$u20$str$GT$::trim::hae704162b917b2f1(rax_4, rdx_2)
0000c375        char var_401 = 0
0000c38d        int64_t input_len = core::str::_$LT$impl$u20$str$GT$::len::h6393c7092af68538(rax_5, rdx_3)
```

Moving to next lines of code
```rs
0000c3a2        if (input_len u<= 0x10)
0000c3e0            void var_400
0000c3e0            core::fmt::Arguments::new_const::h3131d42deb754a2d(&var_400, &data_72c88)
0000c9a5            std::io::stdio::_print::he9dfbe767523a89e(&var_400)
0000c9b2            std::process::exit::h8e2a2cffe2701df2(0)
0000c9b2            noreturn
```
This is just checking whether our input lenth is <= 0x10 or 16 if yes then it executes `std::process::exit::h8e2a2cffe2701df2(0)` which exits the program which we dont want.

Hence i pathced this program to never branch(Hence this condition check is skipped)
**Just right click over the if statement > Goto patch > Choose never branch**

Moving to next lines
```rs
0000c3fc        if ((vault::check_stage_1::hc5f5dd6f49199c6f(rax_5, rdx_3, var_401 & 1) & 1) == 0)
0000c414            void var_3d0
0000c414            core::fmt::Arguments::new_const::h3131d42deb754a2d(&var_3d0, &data_72c88)
0000c43c            std::io::stdio::_print::he9dfbe767523a89e(&var_3d0)
0000c449            std::process::exit::h8e2a2cffe2701df2(0)
0000c449            noreturn
```

Now this calls a function called check_stage_1 on our input is 0 then it branches otherwise it doesnt.
Lets check this function

*check_stage_1*
```rs
0000c030    int64_t vault::check_stage_1::hc5f5dd6f49199c6f(int64_t arg1, int64_t arg2, char arg3)

0000c041        char var_21 = arg3 & 1
0000c045        int64_t rax_1
0000c045        int64_t rdx
0000c045        rax_1, rdx = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c04a        int64_t var_20 = rax_1
0000c04f        int64_t var_18 = rdx
0000c059        char rax_2 = core::iter::traits::iterator::Iterator::any::h82734cf8c4570413()
0000c06b        int64_t rax_3
0000c06b        int64_t rdx_1
0000c06b        rax_3, rdx_1 = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c070        int64_t var_10 = rax_3
0000c075        int64_t var_8 = rdx_1
0000c084        char rcx = core::iter::traits::iterator::Iterator::any::h5d128bfffa89477f()
0000c084        
0000c090        if ((rax_2 & 1) == 0)
0000c092            var_21 = 1
0000c092        
0000c09d        if ((rcx & 1) != 0)
0000c0ac            var_21 = 0
0000c0ac        
0000c0ab        return var_21 & 1

```
Now we can see that it return `var_21 & 1` and we want our function to return a 1, hence we want the first if to always branch while the second to never branch, applying these patches we get,

```rs
0000c030    int64_t vault::check_stage_1::hc5f5dd6f49199c6f(int64_t arg1, int64_t arg2, char arg3)

0000c045        int64_t rax_1
0000c045        int64_t rdx
0000c045        rax_1, rdx = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c04a        int64_t var_20 = rax_1
0000c04f        int64_t var_18 = rdx
0000c067        char var_23 = core::iter::traits::iterator::Iterator::any::h82734cf8c4570413()
0000c06b        int64_t rax_3
0000c06b        int64_t rdx_1
0000c06b        rax_3, rdx_1 = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c070        int64_t var_10 = rax_3
0000c075        int64_t var_8 = rdx_1
0000c08a        char var_22 = core::iter::traits::iterator::Iterator::any::h5d128bfffa89477f()
0000c0ab        return arg3 & 1
```
The decompiler did something weird and is returning `arg3 & 1` , arg3 is a parameter we gave traching it back we see
`if ((vault::check_stage_1::hc5f5dd6f49199c6f(rax_5, rdx_3, var_401 & 1) & 1) == 0)`
and backtracking even more to find 
`char var_401 = 0`

Hence so our function check_stage_1 will always return `0 & 1 = 0` which is exactly what we dont want, hence we invert the check, patch the if statement where the function is getting called, pathc to invert branch so now instead of `== 0` it becomes `!= 0`

Hence this if statement will never branch and quit.

Going to next lines of code.
```rs
0000c429        if (input_len u> 0x10)
0000c48b            void var_398
0000c48b            core::fmt::Arguments::new_const::h3131d42deb754a2d(&var_398, &data_72c98)
0000c982            std::io::stdio::_print::he9dfbe767523a89e(&var_398)
0000c98f            std::process::exit::h8e2a2cffe2701df2(0)
0000c98f            noreturn
```
This is again checking the length of our input, but this time the same input should be greater the 0x10 or 16, if yes then it exits so we patch it to never branch.

Next 
```rs
0000c4a7        if ((vault::check_stage_2::h156d706f48f8f220(rax_5, rdx_3, 0) & 1) == 0)
0000c4bf            void var_368
0000c4bf            core::fmt::Arguments::new_const::h3131d42deb754a2d(&var_368, &data_72c98)
0000c4e1            std::io::stdio::_print::he9dfbe767523a89e(&var_368)
0000c4ee            std::process::exit::h8e2a2cffe2701df2(0)
0000c4ee            noreturn
```
This calls check_stage_2 and if returned value is 0 it branches and quits.
Lets check this check_stage_2

*check_stage_2*
```rs
0000c0c0    int64_t vault::check_stage_2::h156d706f48f8f220(int64_t arg1, int64_t arg2, char arg3)

0000c0d1        char var_21 = arg3 & 1
0000c0d5        int64_t rax_1
0000c0d5        int64_t rdx
0000c0d5        rax_1, rdx = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c0da        int64_t var_20 = rax_1
0000c0df        int64_t var_18 = rdx
0000c0e9        char rax_2 = core::iter::traits::iterator::Iterator::any::hfe3b5d45828ac8ff()
0000c0fb        int64_t rax_3
0000c0fb        int64_t rdx_1
0000c0fb        rax_3, rdx_1 = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c100        int64_t var_10 = rax_3
0000c105        int64_t var_8 = rdx_1
0000c114        char rcx = core::iter::traits::iterator::Iterator::any::hd6a3e960a060f6aa()
0000c114        
0000c120        if ((rax_2 & 1) != 0)
0000c12c            var_21 = 1
0000c12c        
0000c128        if ((rcx & 1) != 0)
0000c13e            var_21 = 0
0000c13e        
0000c13d        return var_21 & 1
```

Same thing here it returns `var_21 & 1` we want to always return 1 hence we always branch the first if and never branch the second. 
After applying the patches 
```rs
0000c0c0    int64_t vault::check_stage_2::h156d706f48f8f220(int64_t arg1, int64_t arg2, char arg3)

0000c0d1        char var_21 = arg3 & 1
0000c0d5        int64_t rax_1
0000c0d5        int64_t rdx
0000c0d5        rax_1, rdx = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c0da        int64_t var_20 = rax_1
0000c0df        int64_t var_18 = rdx
0000c0f7        char var_23 = core::iter::traits::iterator::Iterator::any::hfe3b5d45828ac8ff()
0000c0fb        int64_t rax_3
0000c0fb        int64_t rdx_1
0000c0fb        rax_3, rdx_1 = core::str::_$LT$impl$u20$str$GT$::chars::h5431cd0ad1593657(arg1, arg2)
0000c100        int64_t var_10 = rax_3
0000c105        int64_t var_8 = rdx_1
0000c11a        char var_22 = core::iter::traits::iterator::Iterator::any::hd6a3e960a060f6aa()
0000c13d        return 1
```

perfect, this always returns 1

After this point the program started doing weird things so i saved this new program as `vault_patched` and tried to run it.
And it said `Stage 3 failed!!` so we need to look for more,

Went a little down in code to find where it might be failing us to find this
```rs
0000c621        if ((core::array::equality::_...u5b$T$u5d$$GT$::eq::hb303c1819d1899e8(&var_218, &var_238) & 1) == 0)
0000c63b            void var_a8
0000c63b            core::fmt::Arguments::new_const::h3131d42deb754a2d(&var_a8, &data_72ca8)
0000c6a9            std::io::stdio::_print::he9dfbe767523a89e(&var_a8)
0000c6b6            std::process::exit::h8e2a2cffe2701df2(0)
0000c6b6            noreturn
```
this is checking equality od two variables, i didnt think much and just pathced the if statement to invert branch.
Then is saved and ran it again and gave a random input to get this
```
-----Welcome to the Vault!-----
Enter the secret phrase:
asdf
Stage 3 passed!!
The flag is: apoorvctf{P4tch_1t_L1k3_1t's_H0t}
```
Hope you learned something from this!