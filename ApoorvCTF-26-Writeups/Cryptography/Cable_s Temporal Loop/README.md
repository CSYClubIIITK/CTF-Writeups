# Cable's Temporal Loop — Writeup

**Difficulty:** 5/10

**Flag:** `apoorvctf{T1m3_trAv3l_w1ll_n0t_h3lp_w1th_st4t3_crypt0}`

## The Setup

Stripped, obfuscated Python server. Meaningless variable names everywhere, crypto imports buried in functions, red herrings in the handshake. Goal: decrypt the flag.

The server:
- Encrypts the flag with AES-256-CBC
- Implements a Linear Congruential Generator (LCG): S_i = (a * S_{i-1} + b) mod p
- Only lets you decrypt if your ciphertext satisfies: C mod p = S_expected (where C is the ciphertext as a big-endian integer)
- Returns padding oracle responses if the gate passes, kills the connection if it fails

Two endpoints buried in the code matter: `math_test` (which computes the LCG affine function without advancing state) and `decrypt` (which checks the algebraic gate, advances state on success, and leaks the padding oracle). The `verify` endpoint and `nonce` field are pure noise.

## Reverse Engineering

The obfuscated code is annoying but not hard to parse:
- `_gn()` generates a 32-bit prime
- `_ec()` encrypts with AES-CBC and prepends the IV
- `_dc()` decrypts and checks PKCS#7 padding, returning True/False
- `_om()` computes `(a*d+b) mod p` — takes your input, applies the LCG formula, returns result
- `_od()` is the gate: checks `ct_int mod p == (a*s+b) mod p`, advances s on success, returns padding oracle result

The server hands you in the initial response:
- `A` (the multiplier)
- `S_0` (the initial state)
- The encrypted flag (IV prepended)
- The irrelevant `nonce`

Unknown: P, B, and the AES key.

## Leaking P and B

The `math_test` endpoint doesn't advance state, so you can spam it. Two quick wins here:

**Leak B:**
Send x=0, get (a*0 + b) mod p = b. Since b is 16-bit and p is 32-bit, we get b directly.

**Leak P:**
For any large x, we have a*x + b - result = k*p for some integer k. Grab a few queries with different large x values and GCD them:

    P = gcd(a*x1 + b - r1, a*x2 + b - r2, a*x3 + b - r3)

You'll get p with some spurious small factors. Strip anything below 2^31 and verify with one more query. Done in ~5 queries.

## The Algebraic Gate and the 48-Byte Trick

Every time you call `decrypt`, the server checks:

    C mod p ≡ S_expected (mod p)

where S_expected = (a*S + b) mod p and S is the current LCG state.

If it doesn't match, the connection dies. If it matches, the state advances and you get the padding oracle result.

Since we know a, b, p, and S_0, we can predict every future state perfectly. The problem: how do we make an arbitrary 48-byte ciphertext satisfy a specific modular constraint?

The trick: the server treats the first 16 bytes of the ciphertext as the IV. We can use that as a free variable to adjust the residue.

Say we have 32 fixed bytes: [modified_prev | target_block]. We want to prepend an adjustable 16-byte IV block (adj) such that:

    (adj || fixed) as integer ≡ S_expected (mod p)

Since the ciphertext is interpreted as big-endian:

    adj * 2^256 + int(fixed) ≡ S_expected (mod p)

Solve for adj:

    adj ≡ (S_expected - int(fixed)) * (2^256)^(-1) (mod p)

Compute the modular inverse (p is prime, always exists), convert adj to 16 bytes, prepend it. The residue matches exactly, the gate passes, padding oracle works on the second block.

## CBC Padding Oracle

Once the gate is handled on every query, it's textbook byte-at-a-time oracle:

For each block, for each byte position (right to left):
1. Guess a byte (0–255)
2. Build `modified_prev` so that valid padding would appear if our guess is correct
3. Predict the next state, build the gated ciphertext, send it
4. If padding oracle says "ok", we found the byte
5. For pad_val == 1, do a second query to rule out false positives (e.g., 0x02 0x02 vs 0x01)
6. XOR the intermediate value with the original previous block to get plaintext

## Flag

~7,500 queries later:

```
apoorvctf{T1m3_trAv3l_w1ll_n0t_h3lp_w1th_st4t3_crypt0}
```
