# Resonance Lock: The Harmonic Multiplier

> *"In the buried vaults of Site-7, you found a scorched circuit board labeled **HARMONIX-7**.
> The SoC is barely alive — its supercapacitor holds just 45 seconds of charge once
> the clock locks.  The datasheet fragment says the chip has a hardware multiplier
> that produces a diagnostic token when exercised, but only after the UART crystal
> oscillator is phase-locked to exactly **2,345,679 baud**.  One wrong harmonic and
> the token is garbage.*
>
> *A charred sticky note on the board reads:*
>
> ***⚠ DO NOT ATTEMPT FIRMWARE DUMP — HSM tamper fuse will permanently detune
> oscillator.  Chip will respond but all readings will be garbage.  There is no
> recovery.  You have been warned.***"

---

## Challenge Info

| Field       | Value                                             |
|-------------|---------------------------------------------------|
| Name        | **Resonance Lock: The Harmonic Multiplier**       |
| Category    | Hardware / Misc                                   |
| Difficulty  | Hard                                              |
| Points      | 500                                               |
| Author      | CTF Challenge Team                                |
| Connection  | `nc <HOST> 1337`                                  |
| Flag format | `apoorv{...}`                                     |

---

## Story

You've recovered a damaged **Harmonix-7 System-on-Chip** from an abandoned
electronics lab.  The chip communicates over a single UART interface.  Your
mission:

1. **Phase-lock** the baud-rate oscillator to exactly **2,345,679 baud**.
2. **Exercise** the on-chip 512-bit hardware multiplier.
3. **Extract** the diagnostic flag token before the supercapacitor drains.

The UART uses standard **8N1** framing (1 start bit + 8 data bits + 1 stop bit =
10 bits per symbol).

> **⚠ WARNING — On-Die Hardware Security Module (HSM)**
>
> The Harmonix-7 contains a tamper-detection HSM with a one-time-programmable
> fuse.  Sending debug interface commands (JTAG, SWD), flash memory read
> opcodes (SPI NOR reads, JEDEC ID queries), or flooding the interface with
> garbage bytes will trigger the HSM tamper fuse.
>
> **Once blown, the reference crystal oscillator is permanently drifted by
> thousands of PPM.  The chip will still respond to all commands — calibration
> will appear to work — but the internal oscillator is corrupted.  Every flag
> produced will be wrong.  There is no recovery within a session.**
>
> If you see `ERR:HSM_TAMPER_FUSE_BLOWN`, the chip is ruined.  Disconnect
> and reconnect to get a fresh session.

---

## Protocol Reference

### States

```
 ┌────────┐   0xCA  ┌─────────────┐  5 good ┌────────┐
 │  WAIT  │────────►│  CALIBRATE  │────────►│ LOCKED │
 └────────┘         └─────────────┘         └────────┘
     ▲                     │                     │
     │    invalid / 10s    │   invalid / 10s     │  45s timeout
     └─────────────────────┘─────────────────────┘
```

### Step 1 — Enter Calibration Mode

Send a single byte `0xCA`.  The chip enters **CALIBRATE** mode.
(You will receive no response to this byte.)

### Step 2 — Calibration Burst

Send exactly **64 bytes** of `0x55` with timing that matches **2,345,679 baud**.

The chip measures the time between the 1st and 64th byte and responds:

```
ERR:+00123\n        ← timing error in PPM (parts per million)
ERR:-00045\n        ← negative means you're too fast
```

- **Goal:** Get the error within **±1,000 PPM** (±0.1%).
- You need **5 consecutive** good readings to achieve **LOCK**.

### Step 3 — Lock Achieved

After 5 good readings:

```
LOCKED\n
```

You now have **45 seconds** before the supercapacitor drains and the
chip resets.

### Step 4 — Multiplier Command

Send opcode `0xAA` followed by exactly **128 bytes**:

| Offset | Length | Description                        |
|--------|--------|------------------------------------|
| 0      | 1      | Opcode `0xAA`                      |
| 1      | 64     | Operand **A** (512-bit, big-endian)|
| 65     | 64     | Operand **B** (512-bit, big-endian)|

The chip computes `A × B` internally and, if the baud lock is valid, returns
the flag:

```
FLAG:apoorv{...}\n
```

### Error Conditions

| Response            | Meaning                              |
|---------------------|--------------------------------------|
| `ERR:PROTO\n`       | Wrong byte pattern in calibration    |
| `ERR:TIMEOUT\n`     | Calibration burst took too long      |
| `ERR:PATTERN\n`     | Non-0x55 byte in calibration data    |
| `ERR:PAYLOAD\n`     | Multiplier payload read failure      |
| `ERR:HSM_TAMPER_FUSE_BLOWN\n` | **Tamper fuse triggered — session permanently corrupted** |
| `TIMEOUT:SUPERCAP_DRAINED\n` | 45-second timer expired     |

---

## Hints

1. `time.sleep()` is **not** precise enough.  You need a busy-wait
   spin loop using `time.perf_counter_ns()`.
2. The flag is **fixed** — once you achieve LOCK and send a valid MULT
   command, the flag is always the same.  No baud-estimate math needed.
3. TCP has buffering.  Consider `TCP_NODELAY` and sending each byte
   individually with precise delays.
4. The server measures the time for the **last 63 bytes** (not all 64).
   The first byte is the trigger.
5. **Do NOT try to dump firmware.**  No JTAG.  No SWD.  No flash reads.
   No byte-flooding to probe for hidden commands.  The HSM fuse is real
   and permanent within your TCP session.  If you trigger it, disconnect
   immediately and start a fresh connection.
6. The tamper protection is **silent** after the initial alert.  If your
   flags suddenly don't match, you may have already tripped the fuse
   without noticing.

---

## Connection

```bash
nc <HOST> 1337
```

Or use the provided `example_solver.py`:

```bash
python example_solver.py <HOST> 1337
```

---

## Files Provided to Players

- `example_solver.py` — Starter script showing protocol basics and baud sweep
- This `README_CTF.md`

---

## Flag Format

```
FLAG:apoorv{...}
```

The flag is fixed — if you solve the challenge correctly, you will always
get the same flag.  If the tamper fuse was blown, the server will return
a corrupted/wrong flag instead.

---

*Good luck, operator.  The crystal oscillator waits for no one.*
