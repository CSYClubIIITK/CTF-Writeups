# Rigged Roulette [Cryptography]

**Author:** _Cosmicstar_

## Challenge Description

Welcome to the high-stakes world of Yami Roulette! The dealer swears the game is fair, but something feels... predictable. Turns out, the wheel isn’t as random as it seems. Can you crack the pattern and walk away rich?

## Solution

Looking at the code, it is clear that it is an RSA cracking question. The code generates 2 prime numbers of 512 bits each, then uses them to encrypt the flag and calls the `secret()` function, which converts `p` into byte format (64 bytes). Then it breaks `byte_converted_p` into chunks of 4 bytes each, i.e., 16 blocks (64 bytes/4 bytes). These chunks are converted into long using the `bytes_to_long()` function, and the int value we get is used as a seed to generate an array of 624 elements. Out of that, the function returns values of the array at indexes [0, 1, 2, 227, 228, 229]. This happens with each chunk.

The code prints `n`, `c`, and the `trash` array. We're also given a hint about the initial digit of the seed. So the question is to recover the keys back from the trash, convert individual keys to 4-byte chunks, then append them together and finally convert the 64-byte string to a 512-bit int, which gives `p` back. We'll use this `p` to break RSA, as the decrypt function is already given.

The important aspect of solving this challenge is breaking Python's pseudo-random-number-generator (PRNG), which is already broken. It is unsafe for cryptographic uses as it is easily recoverable with some values of the random array generated. Breaking Python PRNG [this blog post](https://stackered.com/blog/python-random-prediction/) gives a step-by-step approach to break Python PRNG. Scrolling down, we get their GitHub account [here](https://github.com/StackeredSAS/python-random-playground). We need to recover a 32-bit seed, i.e., 4 bytes. We'll use this code to get our keys array back.

This is the code to do that:

```python
import random

def unshiftRight(x, shift):
    res = x
    for i in range(32):
        res = x ^ res >> shift
    return res

def unshiftLeft(x, shift, mask):
    res = x
    for i in range(32):
        res = x ^ (res << shift & mask)
    return res

def untemper(v):
    v = unshiftRight(v, 18)
    v = unshiftLeft(v, 15, 0xefc60000)
    v = unshiftLeft(v, 7, 0x9d2c5680)
    v = unshiftRight(v, 11)
    return v

def invertStep(si, si227):
    X = si ^ si227
    mti1 = (X & 0x80000000) >> 31
    if mti1:
        X ^= 0x9908b0df
    X <<= 1
    mti = X & 0x80000000
    mti1 += X & 0x7FFFFFFF
    return mti, mti1

def recover_Kj_from_Ii(Ii, Ii1, Ii2, i):
    Ji = recover_Ji_from_Ii(Ii, Ii1, i)
    Ji1 = recover_Ji_from_Ii(Ii1, Ii2, i-1)
    return recover_kj_from_Ji(Ji, Ji1, i)

def recover_Ji_from_Ii(Ii, Ii1, i):
    ji = (Ii + i) ^ ((Ii1 ^ (Ii1 >> 30)) * 1566083941)
    ji &= 0xffffffff
    return ji

def init_genrand(seed):
    MT = [0] * 624
    MT[0] = seed & 0xffffffff
    for i in range(1, 623+1):
        MT[i] = ((0x6c078965 * (MT[i-1] ^ (MT[i-1] >> 30))) + i) & 0xffffffff
    return MT

def recover_kj_from_Ji(ji, ji1, i):
    const = init_genrand(19650218)
    key = ji - (const[i] ^ ((ji1 ^ (ji1 >> 30)) * 1664525))
    key &= 0xffffffff
    return key

chunks = [[4094835185, 356762106, 3366297177, 3623603908, 2373193877, 3203846780], [3406548083, 4062546425, 1376818797, 394516489, 3907909298, 3898652639], [1287222167, 2995584073, 1693598779, 811229118, 1707629246, 3304354912], [1243120984, 3460569159, 2340013171, 172985849, 3180767622, 1551040428], [800057846, 2682940396, 123193243, 3036600707, 3794295715, 2393381294], [892967018, 2206189721, 2843934106, 1056160791, 2522099700, 1152632788], [2774545485, 3977855291, 4203604373, 3669198182, 3583908975, 1060491729], [4112967206, 3535798795, 3120649323, 25986165, 2427485753, 1350615610], [318330051, 2236838130, 2496969378, 3525774414, 4069600592, 2282092160], [563544583, 2592975485, 935828735, 2978557025, 2012930992, 995780339], [3460985768, 3379763321, 2949965528, 1505018344, 2512823468, 1021031395], [3394216535, 2529203380, 2768254272, 236994372, 1634295888, 1133018765], [2866010958, 1712165916, 1348052226, 1280486865, 3780769383, 2391071461], [3641791377, 3432968590, 3350590316, 1048613032, 3540539809, 2649316279], [1923548320, 656195356, 4041871255, 2963016066, 3551386262, 3046838184], [2069834435, 1706541602, 4050137025, 857681424, 2381793628, 2665835243]]

for j in chunks:
    for i in range(1):
        random.seed(0x533D0 + i)

        S = [j[0], j[1], j[2], j[3], j[4], j[5]]
        S = [untemper(s) for s in S]

        I_227_, I_228 = invertStep(S[0], S[3])
        I_228_, I_229 = invertStep(S[1], S[4])
        I_229_, I_230 = invertStep(S[2], S[5])

        I_228 += I_228_
        I_229 += I_229_

        seed1 = recover_Kj_from_Ii(I_230, I_229, I_228, 230)
        seed2 = recover_Kj_from_Ii(I_230 + 0x80000000, I_229, I_228, 230)

        print(seed1, seed2)
```

After executing this code, we get this output:
```
86073101 2233556749
3480263105 1332779457
3663810718 1516327070
1146419848 3293903496
812597574 2960081222
1335986148 3483469796
2128181600 4275665248
3346153247 1198669599
2209025034 61541386
3337580270 1190096622
362663341 2510146989
2932032842 784549194
3375914009 1228430361
775335805 2922819453
778684170 2926167818
813242499 2960726147
```

Given the hint, our keys list looks like:
`keys = [2233556749, 1332779457, 3663810718, 1146419848, 2960081222, 3483469796, 2128181600, 3346153247, 61541386, 1190096622, 362663341, 784549194, 3375914009, 2922819453, 2926167818, 2960726147]`

Writing a script to convert keys back to `p` and print the flag:
```python
from Crypto.Util.number import long_to_bytes, bytes_to_long

def decrypt(n, p, c):
    q = n // p
    if p * q != n:
        print("Invalid n")
        return
    phi = (p - 1) * (q - 1)
    d = pow(65537, -1, phi)
    return long_to_bytes(pow(c, d, n))

n = 49812271074113996748256581712467459366588082361636023630564068214612994986892561558381532475755791032675276115848189703815816792642128355747597878537909137779400571814063186968473486503116149991224538115188352954146019052922869981051351571158735260001333011582577193684810211363872980264620807599594086051449
c = 20002117200090813595564977137423791696740924182449971750083551897250822585677154362121434423203173839416183117315744314791189230613149517277553117748654242567572304526577870897931051487912585476465888459445398180637679760443084368095041311696478979083217579778239459905993548371792893219935514397751847671981
keys = [2233556749, 1332779457, 3663810718, 1146419848, 2960081222, 3483469796, 2128181600, 3346153247, 61541386, 1190096622, 362663341, 784549194, 3375914009, 2922819453, 2926167818, 2960726147]

prime_bytes = b''.join(long_to_bytes(k, 4) for k in keys)

p_reconstructed = bytes_to_long(prime_bytes)

print("Reconstructed p:", p_reconstructed)

print(decrypt(n, p_reconstructed, c))
```

Output:
```
Reconstructed p: 6972602544207966251947235635695994030205522047987993616178314841722592376666262323509906093346558040131278962799437242718155851841922133993388359101782147
b'apoorvctf{wh0_needs_luck_wh3n_y0u_h4ve_math}'
```

Hurray!! We got our flag back.

The flag is `apoorvctf{wh0_needs_luck_wh3n_y0u_h4ve_math}`
