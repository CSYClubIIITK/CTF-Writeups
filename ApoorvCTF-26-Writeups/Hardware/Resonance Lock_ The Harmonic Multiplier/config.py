"""
config.py — All evil constants for the Harmonix-7 SoC emulation.

Every timing / protocol / crypto constant lives here.
Touch these and the flag changes. That's the point.
"""

# ─── UART Emulation ────────────────────────────────────────────────
TARGET_BAUD        = 2345679          # The one true baud rate (bits/sec)
BIT_TIME_NS        = int(1e9 / TARGET_BAUD)  # ~426.30 ns per bit
FRAME_BITS         = 10               # 1 start + 8 data + 1 stop (no parity)

# ─── Calibration ───────────────────────────────────────────────────
CALIBRATE_OPCODE   = 0xCA             # Enter CALIBRATE mode
CALIBRATE_PATTERN  = 0x55             # Byte to send during calibration
CALIBRATE_COUNT    = 64               # Number of 0x55 bytes required
PPM_TOLERANCE      = 1000             # ±1000 ppm = ±0.1 %
GOOD_LOCK_COUNT    = 5                # Consecutive good readings to lock

# ─── Multiplier ────────────────────────────────────────────────────
MULT_INIT_OPCODE   = 0xAA             # MULT-INIT opcode
MULT_PAYLOAD_LEN   = 128              # 64 bytes A + 64 bytes B  (512-bit each)
OPERAND_LEN        = 64               # bytes per operand

# ─── Flag ─────────────────────────────────────────────────────
# Fixed flag returned when the challenge is solved (LOCKED + valid MULT).
# LeetSpeak for "harmonic resonance unlocked".
FIXED_FLAG          = "apoorv{3N7R0P1C_31D0L0N_0F_7H3_50C_4N4LY57_N0C7URN3}"

# Legacy constants kept for reference (no longer used in flag derivation)
MODULUS_MAGIC       = 0x1337C0DE1337C0DE
FLAG_XOR_MASK       = 0xC0FFEE
FLAG_BYTE_LEN       = 32              # flag is 32 bytes = 64 hex chars

# ─── Anti-Tamper / Firmware Dump Protection ───────────────────────
# The Harmonix-7 has an on-die HSM.  Probing the debug bus or
# sending firmware-dump opcodes (JTAG, SWD, SPI flash reads)
# blows a one-time fuse that permanently drifts the reference
# oscillator.  The chip still *responds* — but every flag is wrong.

# Bytes that look like debug/dump commands (instant tamper triggers)
DUMP_OPCODES = frozenset([
    0x03,   # SPI NOR "Read Data"
    0x0B,   # SPI NOR "Fast Read"
    0x9F,   # JEDEC Read ID
    0x90,   # Read Manufacturer ID
    0x5A,   # Read SFDP
    0xAB,   # Release Power-Down / Device ID
    0xB9,   # Deep Power-Down
    0x06,   # Write Enable (flash)
    0x20,   # Sector Erase
    0xD8,   # Block Erase
    0xC7,   # Chip Erase
    0x02,   # Page Program
    0x35,   # Read Status Register-2
    0x05,   # Read Status Register-1
    0x3B,   # Dual Output Fast Read
    0x6B,   # Quad Output Fast Read
    0xBB,   # Dual I/O Fast Read
    0xEB,   # Quad I/O Fast Read
    0x4B,   # Read Unique ID
    0x48,   # Read Serial Flash Discovery Parameter
    0x77,   # Set Burst with Wrap
    0xE7,   # Word Read Quad I/O
    0x14,   # JTAG IDCODE
    0x1C,   # JTAG BYPASS
    0xFF,   # JTAG reset / bus scan
    0xFE,   # SWD line reset sentinel
    0x00,   # SWD / JTAG all-zeros probe
    0xA5,   # SWD magic preamble
])

# Tamper scoring — how quickly does the fuse blow?
TAMPER_SCORE_DUMP_OPCODE  = 25        # Known dump opcode = instant pain
TAMPER_SCORE_INVALID      = 5         # Generic invalid byte
TAMPER_SCORE_FLOOD        = 10        # Too many bytes too fast
TAMPER_THRESHOLD          = 50        # Score ≥ this → fuse blown
FLOOD_WINDOW_SEC          = 2.0       # Time window for flood detection
FLOOD_BYTE_LIMIT          = 20        # More than this in window = flood

# Once tampered, the oscillator drifts by this many PPM (random per session)
TAMPER_DRIFT_MIN_PPM      = 5000      # Minimum permanent drift
TAMPER_DRIFT_MAX_PPM      = 50000     # Maximum permanent drift

# ─── Timing / Limits ──────────────────────────────────────────────
LOCKED_TIMEOUT_SEC  = 45              # Supercapacitor drain timer
INVALID_RESET_SEC   = 10              # Reset-to-WAIT on bad input
LISTEN_PORT         = 1337            # TCP port exposed by Docker

# ─── Banner (server-side only — players never see this) ───────────
BOOT_BANNER         = "Harmonix-7 online"
