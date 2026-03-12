# Domino - Noisy Padding Oracle Challenge

**Difficulty:** 9/10

**Files:** `challenge.py`

**Flag:** `APOORVCTF{Pr0b4ility_mAnipul4ti0n_w0u1d_h4V3_m4de_1t_e4sier}`

## Challenge Overview

The server encrypts a 16-byte hex string (32 printable characters) with AES-CBC and lets you query a padding oracle. The catch: the oracle is intentionally noisy—it gives correct responses only 55% of the time (45% noise threshold). You get 10,000 queries to recover the plaintext before hitting the query limit or Azure container timeout.

## The Attack Path

### 1. Padding Oracle Basics
The server accepts a ciphertext for verification. If decryption and unpadding succeeds, it returns `true`; otherwise, `false`. Normally this is trivial—one valid candidate per byte. But with noise, you need statistics.

### 2. The Hex Constraint
The plaintext is always valid hex (16 bytes = 32 hex chars in ASCII: `0-9a-f`). This is the key insight: instead of guessing 256 possible byte values, you only have 16 valid candidates per byte position. **This cuts the search space dramatically.**

For each byte, you iterate through all 256 possible values, but only keep those where the XOR of `(brute_byte ^ padding_value ^ prev_block_byte)` decodes to a valid hex character. That typically leaves around 16 candidates.

### 3. Information Theory & Bayesian Filtering
For each candidate, you track a log-likelihood ratio:
- `LOG_TRUE = log(0.55 / 0.45)` (response favors this candidate)
- `LOG_FALSE = log(0.45 / 0.55)` (response disfavors this candidate)

With each query, add the appropriate log value to the candidate's score. After enough queries, compute softmax over all log-ratios to get posterior probabilities.

### 4. Query Budget Strategy
The critical part: you need to stay under the query limit while maintaining confidence. We allocate **~312 queries per byte on average** (32 bytes × 312 ≈ 10,000 queries strict).

- **Baseline phase:** Query all 16 candidates 5 times each (~80 queries). This gives initial signal.
- **Information loop:** Query the top candidate (and occasionally the runner-up) until either confidence exceeds 0.93 or cumulative budget ceiling is hit.
- **Cumulative budget:** Each byte position `i` is allowed to consume up to `(i+1) × 312` queries total. This prevents hard bytes from exceeding the global limit.

### 5. Server Timeout Considerations
The Azure container has a 4-minute hard timeout. Exceed the query limit or spin too aggressively, and the container kills the connection. But there's more: the server maintains a **queue (pq)** that allocates points based on request frequency. If you hit too many requests without proper throttling, the pq points accumulate and the server locks you out for a calculated duration. If you disconnect due to the Azure timeout, your pq points decay—but not fast enough to recover if you immediately retry with the same naive approach.

The key insight: **don't just spam the oracle like a dumb AI would.** Proper Bayesian filtering converges quickly with correlated responses (55% accuracy). Generic scripts without understanding candidate removal math will need way too many requests and hit the timeout every single time. You literally have to understand how candidate filtering scales to keep request count low enough to survive the 4-minute container window.

## The Exploit

1. Connect to the server and get an initial ciphertext.
2. For each 16-byte block, recover plaintext byte-by-byte from right to left (standard CBC padding oracle).
3. For each position, filter candidates to the hex charset, query strategically using Bayesian inference, and stop when confident or budget-limited.
4. XOR results properly to account for CBC mode and padding.
5. Submit the recovered plaintext to get the flag.

The math is tuned such that a random oracle (50/50 guessing) would need exponentially more queries, but with even slightly correlated responses (55%), Bayesian inference converges quickly on the true candidate.
