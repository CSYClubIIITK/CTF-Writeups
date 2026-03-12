## TICK TOCK [Cryptography]

**Author:** _orangcar_

## Challenge Description

The service asks for a password and returns the flag only on exact match.
At first glance this looks brute-force resistant, but the password check leaks timing information.

## Solution

This is a classic timing side-channel in string comparison.

From [`main.go`](/home/aditya17/Aditya/ApoorvCTF/2026/time_oracle/TICK_TOCK_writeup/challenge/main.go), the vulnerable logic is:

```go
func check(input, password string) bool {
	for i := 0; i < len(password); i++ {
		if i >= len(input) {
			return false
		}
		if input[i] != password[i] {
			return false
		}
		time.Sleep(1000 * time.Millisecond)
	}
	return len(input) == len(password)
}
```

For every correct character at the same position, the server sleeps 1 second before checking the next byte.
So if our guess has a longer correct prefix, server response time is longer.

### Attack idea

1. Connect once and wait for `Please enter the password:`.
2. Recover password prefix one character at a time.
3. For each next position, try all candidates (here digits `0-9`).
4. Measure response time for `known_prefix + candidate`.
5. Candidate with maximum time is the correct next byte.
6. Repeat until server returns `Correct! <flag>`.

### Why this works

- Wrong first byte returns almost immediately.
- Correct first byte + wrong second byte costs about 1 second.
- Correct first two bytes + wrong third byte costs about 2 seconds.
- This gives a clean oracle for prefix length, so full password recovery is straightforward.

### Exploit

Solver script is included at:

- [`solution.py`](/home/aditya17/Aditya/ApoorvCTF/2026/time_oracle/TICK_TOCK_writeup/solution.py)

Challenge files are copied here:

- [`challenge/main.go`](/TICK_TOCK_writeup/challenge/main.go)
- [`challenge/dockerfile`](/TICK_TOCK_writeup/challenge/dockerfile)
- [`challenge/go.mod`](/TICK_TOCK_writeup/challenge/go.mod)
- [`challenge/go.sum`](/TICK_TOCK_writeup/challenge/go.sum)

### Steps to run challenge locally:

```bash
docker build -t tick-tock . 
docker run -d --name tick-tock  -p 9001:9001 --env-file .env tick-tock
python solution.py
```

### Connecto challenge at:
```
nc localhost 9001
```

