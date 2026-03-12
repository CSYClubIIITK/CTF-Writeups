# OPERATION SKYFALL — COMPLETE SOLUTION

### Classification: ORGANISER ONLY — DO NOT DISTRIBUTE

---

> **FLAG:** `apoorvctf{skyblue_4uct10n_l1nk_d3c0d3d}`

---

## Challenge Architecture

The IQ file is a 4-second, zero-noise complex float32 recording at **2,048,000 samples/sec** containing two signal bursts designed as a two-stage puzzle:

| Burst | Time | Freq Offset | Modulation | Encoding | Content |
|-------|------|-------------|------------|----------|---------|
| 1 | 0.1 s | +50 kHz | OOK / ASK | Manchester (IEEE 802.3) | CC1101 register hex dump |
| 2 | 3.0 s | −200 kHz | 2-FSK | NRZ | ASCII flag |

Signal 1 is the key to Signal 2. Participants must fully decode and interpret Signal 1 before they can even attempt Signal 2. There is a deliberate ~2.9-second silent gap between them.

---

## Progressive Hint System

Release these hints at timed intervals during the competition to prevent rage-quits while maintaining difficulty.

### Tier 1 — Gentle nudges (release after 2 hours)

| # | Hint |
|---|------|
| 1 | *"The filename isn't just a label."* |
| 2 | *"Two bursts, two problems. Solve the first to unlock the second."* |

### Tier 2 — Directional (release after 4 hours)

| # | Hint |
|---|------|
| 3 | *"The first signal goes on and off. Literally."* |
| 4 | *"Manchester isn't just a city — it's a code."* |
| 5 | *"The hex dump you get isn't random. It's a register configuration for a very specific chip."* |

### Tier 3 — Technical (release after 6 hours)

| # | Hint |
|---|------|
| 6 | *"TI makes a sub-GHz transceiver that operates in the 433 MHz ISM band. It starts with CC and ends with 1101."* |
| 7 | *"FREQ2, FREQ1, FREQ0. MDMCFG4, MDMCFG3, MDMCFG2. DEVIATN. SYNC1, SYNC0. Read the datasheet."* |
| 8 | *"The registers tell you the modulation, baud rate, deviation, and sync word for the second signal."* |

### Tier 4 — Last resort (release after 8 hours)

| # | Hint |
|---|------|
| 9 | *"Signal 1: ASK, 10k baud, Manchester. Signal 2: 2-FSK, ~9600 baud, sync 0xD391. The offset between them is large."* |

---

## Full Walkthrough

### Step 0: Determine the Sample Rate

The filename `challenge_2048k_cf32.iq` encodes both the sample rate and the format:
- **2048k** → 2,048,000 samples per second
- **cf32** → complex float32, interleaved I/Q (little-endian)

Participants must figure this out themselves. Loading the file:
```python
import numpy as np
raw = np.fromfile("challenge_2048k_cf32.iq", dtype=np.float32)
iq = raw[0::2] + 1j * raw[1::2]
# 8,192,000 samples → 4.0 seconds at 2.048 MSps
```

### Step 1: Visual Inspection

Open in **URH**, **Inspectrum**, or plot in Python:
- Set sample rate to **2,048,000 Hz**
- The spectrogram/waterfall reveals:
  - **Burst 1** at ~0.1 s — a carrier toggling on/off at **+50 kHz** from centre
  - **Silence** for ~2.9 seconds
  - **Burst 2** at ~3.0 s — a frequency-shifting signal at **−200 kHz** from centre

The two signals are at completely different frequency offsets and use different modulations. This is the first major observation participants must make.

### Step 2: Demodulate Signal 1 (OOK + Manchester)

**In URH:**
1. Zoom into the first burst (~0.1 s mark)
2. URH's auto-detect will likely identify it as **ASK/OOK**
3. Samples per symbol: **~205** (i.e., 2,048,000 / 10,000 = 204.8)
4. Demodulate → raw bitstream
5. The bitstream has a distinctive pattern: runs of alternating bits that are exactly **twice** the expected data rate. This is the hallmark of **Manchester encoding**.
6. Apply Manchester decoding (IEEE 802.3 convention: `01 → 0`, `10 → 1`)

**Decoded hex output:**
```
AA AA AA AA 2D D4 18 00 29 04 D3 05 91 06 3D 08 05 0D 10 0E A7 0F 62 10 88 11 83 12 02 15 40 CA
```

### Step 3: Parse the Packet Frame

The frame follows a standard packet radio structure:

| Field | Hex | Interpretation |
|-------|-----|----------------|
| Preamble | `AA AA AA AA` | Standard alternating-bit preamble (4 bytes) |
| Sync word | `2D D4` | CC1101 default sync word — **this is the critical clue** |
| Length | `18` | 24 bytes of payload follow |
| Payload | `00 29 04 D3 ... 15 40` | 12 pairs of (register address, value) |
| CRC | `CA` | XOR checksum of payload bytes |

The sync word `0x2DD4` is the factory default for the **Texas Instruments CC1101** sub-GHz transceiver. This is the "aha" moment for the participant — they now know what chip they're dealing with.

### Step 4: Decode the CC1101 Register Dump

Each payload pair is `(register_address, register_value)`. Using the **CC1101 datasheet** (TI document SWRS061I):

| Address | Value | Register | Purpose |
|---------|-------|----------|---------|
| `0x00` | `0x29` | IOCFG2 | GDO2 output pin configuration (cosmetic) |
| `0x04` | `0xD3` | **SYNC1** | Sync word high byte for target radio link |
| `0x05` | `0x91` | **SYNC0** | Sync word low byte for target radio link |
| `0x06` | `0x3D` | PKTLEN | Max packet length = 61 bytes |
| `0x08` | `0x05` | PKTCTRL0 | Variable-length packets, CRC enabled |
| `0x0D` | `0x10` | **FREQ2** | Frequency word bits [23:16] |
| `0x0E` | `0xA7` | **FREQ1** | Frequency word bits [15:8] |
| `0x0F` | `0x62` | **FREQ0** | Frequency word bits [7:0] |
| `0x10` | `0x88` | **MDMCFG4** | Channel filter BW + data rate exponent |
| `0x11` | `0x83` | **MDMCFG3** | Data rate mantissa |
| `0x12` | `0x02` | **MDMCFG2** | Modulation format + sync mode |
| `0x15` | `0x40` | **DEVIATN** | FSK frequency deviation |

### Step 5: Calculate Signal 2 Parameters

All formulas below come directly from the CC1101 datasheet.

#### Carrier Frequency

```
FREQ[23:0] = (FREQ2 << 16) | (FREQ1 << 8) | FREQ0
           = (0x10 << 16) | (0xA7 << 8) | 0x62
           = 0x10A762
           = 1,091,426

f_carrier = (f_xosc / 2^16) × FREQ
          = (26,000,000 / 65,536) × 1,091,426
          = 396.7285... × 1,091,426
          ≈ 433.00 MHz
```

#### Data Rate

```
DRATE_E = MDMCFG4[3:0] = 0x88 & 0x0F = 0x08 = 8
DRATE_M = MDMCFG3      = 0x83        = 131

R_data = ((256 + DRATE_M) × 2^DRATE_E / 2^28) × f_xosc
       = ((256 + 131) × 256 / 268,435,456) × 26,000,000
       = (387 × 256 / 268,435,456) × 26,000,000
       = (99,072 / 268,435,456) × 26,000,000
       = 0.0003691... × 26,000,000
       ≈ 9,596 baud (effectively 9,600 baud)
```

#### Modulation Format

```
MOD_FORMAT = MDMCFG2[6:4] = (0x02 >> 4) & 0x07 = 0

Lookup table (CC1101 datasheet Table 36):
  0 = 2-FSK    ← this one
  1 = GFSK
  3 = ASK/OOK
  4 = 4-FSK
  7 = MSK
```

#### Frequency Deviation

```
DEVIATION_E = (DEVIATN >> 4) & 0x07 = (0x40 >> 4) & 0x07 = 4
DEVIATION_M = DEVIATN & 0x07        = 0x40 & 0x07          = 0

f_dev = (f_xosc / 2^17) × (8 + DEVIATION_M) × 2^DEVIATION_E
      = (26,000,000 / 131,072) × (8 + 0) × 16
      = 198.364... × 128
      = 25,390.6 Hz ≈ 25.4 kHz
```

#### Sync Word for Signal 2

```
SYNC1 = 0xD3
SYNC0 = 0x91
Sync word = 0xD391
```

### Step 6: Demodulate Signal 2 (2-FSK)

Armed with the parameters from Signal 1:

**In URH:**
1. Navigate to the second burst (~3.0 s)
2. Set modulation to **FSK**
3. Set samples per symbol to **~213** (= 2,048,000 / 9,600)
4. Demodulate the FSK signal
5. Search for the sync word **`D3 91`** in the hex view
6. The byte immediately after the sync word is the **length** (0x27 = 39)
7. The next 39 bytes are the ASCII flag

**In Python (manual FM demod):**
```python
# Extract burst 2 region, shift to baseband at -200 kHz
sig2 = iq[2.9s : 3.15s]
sig2_bb = sig2 * exp(-j * 2π * (-200000) * t)

# Instantaneous frequency via phase derivative
phase = unwrap(angle(sig2_bb))
freq_inst = diff(phase) / (2π) * sample_rate

# Threshold at zero → bit decisions
# Sample at 9600 baud intervals
# Find sync word D391, extract ASCII
```

### Step 7: Read the Flag

```
Frame structure:
  AA AA AA AA AA AA AA AA   ← 8-byte preamble (0xAA)
  D3 91                     ← sync word
  27                        ← length = 39 bytes
  61 70 6F 6F 72 76 63 74   ← "apoorvct"
  66 7B 73 6B 79 62 6C 75   ← "f{skyblu"
  65 5F 34 75 63 74 31 30   ← "e_4uct10"
  6E 5F 6C 31 6E 6B 5F 64   ← "n_l1nk_d"
  33 63 30 64 33 64 7D      ← "3c0d3d}"
  14                        ← CRC byte
```

**Flag: `apoorvctf{skyblue_4uct10n_l1nk_d3c0d3d}`**

---

## Expected Difficulty Barriers

These are the walls participants will hit, in order:

1. **Figuring out the sample rate** — the only clue is the filename. No metadata is provided.
2. **Identifying two separate signals** — they must inspect the spectrogram and realize there are two bursts at different frequency offsets.
3. **Recognizing OOK modulation** — the first signal is on/off keyed. URH can auto-detect this.
4. **Recognizing Manchester encoding** — after ASK demod, the bitstream looks "wrong" until they realize it's Manchester-coded. The doubled symbol rate is the giveaway.
5. **Identifying the CC1101 chip** — the sync word `0x2DD4` is the key. Searching "2DD4 radio sync" or recognizing the register addresses requires RF domain knowledge.
6. **Reading the CC1101 datasheet** — participants must correctly apply the frequency, data rate, and modulation formulas. This is the core challenge.
7. **Applying those parameters to Signal 2** — they need to set up FSK demodulation with the correct baud rate, deviation, and sync word for a signal that's at a completely different frequency offset.
8. **Extracting ASCII from the demodulated bytes** — straightforward once they have clean bits.

## Technical Parameters (Quick Reference)

| Parameter | Signal 1 | Signal 2 |
|-----------|----------|----------|
| Time position | 0.1 s | 3.0 s |
| Carrier offset | +50 kHz | −200 kHz |
| Modulation | OOK / ASK | 2-FSK |
| Symbol rate | 10,000 baud | ~9,600 baud |
| Samples/symbol | 205 | 213 |
| Encoding | Manchester (IEEE 802.3) | NRZ |
| FSK deviation | N/A | 25.4 kHz |
| Sync word | 0x2DD4 | 0xD391 |
| Preamble | AA AA AA AA | AA AA AA AA AA AA AA AA |
| Content | CC1101 register dump | ASCII CTF flag |

---

## Recommended Tools for Participants

*(Do not share this list — let them figure out what tools they need)*

| Tool | What it solves |
|------|----------------|
| URH | Both signals — ASK auto-detect, FSK demod, Manchester decode, hex view |
| Inspectrum | Visual inspection, measuring symbol rates from waterfall |
| GNU Radio | Custom flowgraph for FSK demod with exact parameters |
| Python + NumPy | Manual signal processing, hex parsing, CRC verify |
| CC1101 Datasheet (SWRS061I) | Register address map, frequency/datarate/modulation formulas |

---

**END OF SOLUTION DOCUMENT**
