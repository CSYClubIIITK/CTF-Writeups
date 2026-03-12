"""
device.py — Harmonix-7 SoC Emulator (State-Machine UART Server)

This is the main challenge server.  It listens on TCP port 1337
and speaks a byte-stream protocol that emulates a UART peripheral
on the fictional Harmonix-7 System-on-Chip.

States
------
  WAIT       → Idle. Only 0xCA transitions to CALIBRATE.
  CALIBRATE  → Expecting 64 × 0x55 bytes.  Measures timing PPM.
  LOCKED     → Baud rate locked.  Accepts 0xAA + 128-byte multiplier payload.

Anti-Tamper (Firmware Dump Protection)
--------------------------------------
  The Harmonix-7 has an on-die HSM with a one-time-programmable fuse.
  Sending debug/dump opcodes (JTAG, SWD, SPI flash reads) or flooding
  the bus with garbage triggers the fuse.  Once blown, the reference
  crystal oscillator is permanently drifted by thousands of PPM.
  The chip still RESPONDS to all commands — but the calibration is
  silently corrupted, so every flag will be wrong.  No error message
  is given after the initial tamper alert.  This is intentional evil.

Evil bits
---------
  * Timing is measured with time.perf_counter_ns() to nanosecond
    precision.  Drift accumulates — even a few-hundred-ppm error
    will corrupt the modulus and thus the flag.
  * A 45-second supercapacitor timeout drains the LOCKED state.
  * Any protocol violation resets to WAIT after 10 s.
  * Firmware dump attempts blow the tamper fuse permanently.

Run:
    python device.py          (standalone)
    docker compose up         (via Docker)
"""

import asyncio
import logging
import random
import struct
import time
from collections import deque
from typing import Optional

import config as C

# ─── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
)
log = logging.getLogger("harmonix7")


# ═══════════════════════════════════════════════════════════════════
#  Per-connection session
# ═══════════════════════════════════════════════════════════════════

class Session:
    """
    One session per TCP connection.  Tracks the full state machine.
    """

    # States
    WAIT      = "WAIT"
    CALIBRATE = "CALIBRATE"
    LOCKED    = "LOCKED"

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.state  = self.WAIT

        # Calibration bookkeeping
        self.good_count: int = 0
        self.ppm_readings: list[float] = []
        self.locked_baud_estimate: Optional[float] = None

        # Timeout handles
        self._locked_timeout_task: Optional[asyncio.Task] = None
        self._invalid_reset_task:  Optional[asyncio.Task] = None

        # ── Anti-Tamper / Firmware Dump Protection ─────────────────
        # Once the tamper fuse is blown, it stays blown for the
        # entire TCP session.  No reconnect-within-session healing.
        self.tamper_score: int = 0
        self.tamper_fuse_blown: bool = False
        self.tamper_drift_ppm: float = 0.0   # permanent oscillator drift
        self.tamper_alerted: bool = False     # only warn once

        # Flood detection: track timestamps of recent invalid bytes
        self._recent_invalid_times: deque = deque()

        # Peer info for logging
        peername = writer.get_extra_info("peername")
        self.tag = f"{peername[0]}:{peername[1]}" if peername else "unknown"

    # ── Helpers ────────────────────────────────────────────────────

    async def send(self, data: bytes | str):
        """Send data to the player (bytes or UTF-8 string)."""
        if isinstance(data, str):
            data = data.encode()
        self.writer.write(data)
        await self.writer.drain()

    def _reset(self, reason: str):
        """Reset to WAIT, clearing all calibration state."""
        log.info("[%s] RESET → WAIT (%s)", self.tag, reason)
        self.state = self.WAIT
        self.good_count = 0
        self.ppm_readings.clear()
        self.locked_baud_estimate = None
        self._cancel_timers()

    def _cancel_timers(self):
        for t in (self._locked_timeout_task, self._invalid_reset_task):
            if t and not t.done():
                t.cancel()

    # ── Anti-Tamper Engine ─────────────────────────────────────────

    async def _record_tamper(self, byte: int, score: int, reason: str):
        """
        Accumulate tamper score.  Once threshold is reached, blow the
        fuse — permanently inject a random oscillator drift (thousands
        of PPM).  The chip will still respond to all commands, but
        the calibration will be silently wrong forever.
        """
        self.tamper_score += score
        log.warning("[%s] TAMPER +%d (0x%02X %s) total=%d/%d",
                    self.tag, score, byte, reason,
                    self.tamper_score, C.TAMPER_THRESHOLD)

        if self.tamper_score >= C.TAMPER_THRESHOLD and not self.tamper_fuse_blown:
            self._blow_tamper_fuse()

    def _blow_tamper_fuse(self):
        """
        Irreversible for this session.  Pick a random drift that makes
        calibration impossible to match the true baud rate.
        The sign is also random — sometimes fast, sometimes slow.
        """
        sign = random.choice([-1, 1])
        drift = random.randint(C.TAMPER_DRIFT_MIN_PPM, C.TAMPER_DRIFT_MAX_PPM)
        self.tamper_drift_ppm = sign * drift
        self.tamper_fuse_blown = True

        log.critical("[%s] ██ TAMPER FUSE BLOWN ██  drift=%+d PPM  "
                     "(oscillator permanently corrupted for this session)",
                     self.tag, self.tamper_drift_ppm)

    async def _tamper_alert_once(self):
        """
        Send a single cryptic warning.  After this, the chip goes
        silent about the tamper — it just gives wrong results.
        """
        if not self.tamper_alerted:
            self.tamper_alerted = True
            await self.send("ERR:HSM_TAMPER_FUSE_BLOWN\n")

    def _check_flood(self) -> bool:
        """
        Detect byte flooding — too many bytes in a short time window.
        Returns True if flood is detected.
        """
        now = time.monotonic()
        self._recent_invalid_times.append(now)

        # Prune old entries outside the window
        while (self._recent_invalid_times and
               now - self._recent_invalid_times[0] > C.FLOOD_WINDOW_SEC):
            self._recent_invalid_times.popleft()

        return len(self._recent_invalid_times) > C.FLOOD_BYTE_LIMIT

    async def _process_suspicious_byte(self, byte: int):
        """
        Evaluate a byte for tamper/dump indicators and score it.
        Called on every invalid/unexpected byte in any state.
        """
        if byte in C.DUMP_OPCODES:
            await self._record_tamper(
                byte, C.TAMPER_SCORE_DUMP_OPCODE,
                "dump/debug opcode")
        else:
            await self._record_tamper(
                byte, C.TAMPER_SCORE_INVALID,
                "invalid byte")

        # Check for flooding (rapid-fire garbage bytes)
        if self._check_flood():
            await self._record_tamper(
                byte, C.TAMPER_SCORE_FLOOD,
                "flood detected")

        # Alert if fuse just blew
        if self.tamper_fuse_blown:
            await self._tamper_alert_once()

    # ── Timeout coroutines ─────────────────────────────────────────

    async def _locked_timeout(self):
        """Supercapacitor drain — 45 s after LOCKED, reset."""
        await asyncio.sleep(C.LOCKED_TIMEOUT_SEC)
        log.info("[%s] Supercapacitor drained — LOCKED timeout", self.tag)
        await self.send("TIMEOUT:SUPERCAP_DRAINED\n")
        self._reset("supercap timeout")

    async def _invalid_reset(self):
        """On invalid data, wait 10 s then reset to WAIT."""
        await asyncio.sleep(C.INVALID_RESET_SEC)
        self._reset("invalid input timeout")

    # ── Timing measurement (the evil part) ─────────────────────────

    def _measure_ppm(self, elapsed_ns: int, byte_count: int) -> float:
        """
        Compute the timing error in PPM.

        Expected time = byte_count * FRAME_BITS * BIT_TIME_NS
        PPM = ((actual - expected) / expected) * 1_000_000

        If the tamper fuse is blown, silently inject permanent drift
        into the measurement.  The reported PPM will look normal-ish
        but the internal baud estimate will be wrong.
        """
        expected_ns = byte_count * C.FRAME_BITS * C.BIT_TIME_NS
        if expected_ns == 0:
            return 999999.0
        raw_ppm = ((elapsed_ns - expected_ns) / expected_ns) * 1_000_000

        # ── Tamper injection (silent corruption) ───────────────────
        # If fuse is blown, we ADD the drift to the raw measurement.
        # The player sees a "normal" ERR value, but the internal
        # baud estimate used for the flag will be wrong.
        if self.tamper_fuse_blown:
            raw_ppm += self.tamper_drift_ppm
            log.debug("[%s] Tamper drift injected: %+d PPM (player sees %+.0f)",
                      self.tag, self.tamper_drift_ppm, raw_ppm)
        return raw_ppm

    @staticmethod
    def _estimate_baud(elapsed_ns: int, byte_count: int) -> float:
        """
        Reverse-calculate the player's effective baud from elapsed time.
        baud = (byte_count * FRAME_BITS * 1e9) / elapsed_ns
        """
        total_bits = byte_count * C.FRAME_BITS
        if elapsed_ns == 0:
            return 0.0
        return (total_bits * 1_000_000_000) / elapsed_ns

    # ── State handlers ─────────────────────────────────────────────

    async def handle_wait(self, byte: int):
        """WAIT state — only 0xCA is accepted."""
        if byte == C.CALIBRATE_OPCODE:
            self.state = self.CALIBRATE
            self.good_count = 0
            self.ppm_readings.clear()
            log.info("[%s] → CALIBRATE mode", self.tag)
        else:
            # ── Tamper detection: suspicious byte in WAIT ──────────
            await self._process_suspicious_byte(byte)

            # Schedule a 10-s reset
            log.warning("[%s] Invalid byte 0x%02X in WAIT", self.tag, byte)
            self._invalid_reset_task = asyncio.ensure_future(self._invalid_reset())

    async def handle_calibrate(self, first_byte: int):
        """
        CALIBRATE state — read 64 × 0x55 (first byte already consumed).
        Measure total reception time to compute PPM error.
        """
        # The first byte of the 64-byte burst has already been read.
        if first_byte != C.CALIBRATE_PATTERN:
            log.warning("[%s] Bad calibrate byte 0x%02X (expected 0x55)", self.tag, first_byte)
            await self.send("ERR:PROTO\n")
            self._invalid_reset_task = asyncio.ensure_future(self._invalid_reset())
            return

        # Start nanosecond timer
        t0 = time.perf_counter_ns()

        # Read remaining 63 bytes
        remaining = C.CALIBRATE_COUNT - 1  # 63
        try:
            data = await asyncio.wait_for(
                self.reader.readexactly(remaining),
                timeout=5.0,
            )
        except (asyncio.TimeoutError, asyncio.IncompleteReadError):
            log.warning("[%s] Calibration read timeout/short", self.tag)
            await self.send("ERR:TIMEOUT\n")
            self._reset("calibration read failure")
            return

        t1 = time.perf_counter_ns()
        elapsed_ns = t1 - t0

        # Validate all bytes are 0x55
        bad_bytes = [b for b in data if b != C.CALIBRATE_PATTERN]
        if bad_bytes:
            log.warning("[%s] Non-0x55 byte in calibration burst", self.tag)
            # ── Tamper: every bad byte in the burst is suspicious ──
            for b in bad_bytes:
                await self._process_suspicious_byte(b)
            await self.send("ERR:PATTERN\n")
            self._invalid_reset_task = asyncio.ensure_future(self._invalid_reset())
            return

        # ── Compute PPM error ──────────────────────────────────────
        # Note: we measure the 63 remaining bytes (first byte was the trigger).
        ppm = self._measure_ppm(elapsed_ns, remaining)
        baud_est = self._estimate_baud(elapsed_ns, remaining)

        sign = "+" if ppm >= 0 else "-"
        ppm_abs = abs(int(round(ppm)))
        err_str = f"ERR:{sign}{ppm_abs:05d}\n"
        await self.send(err_str)
        log.info("[%s] PPM=%+.1f  baud_est=%.2f  (%s)",
                 self.tag, ppm, baud_est, err_str.strip())

        # ── Check if within tolerance ──────────────────────────────
        if abs(ppm) <= C.PPM_TOLERANCE:
            self.good_count += 1
            self.ppm_readings.append(ppm)
            log.info("[%s] Good reading %d/%d", self.tag, self.good_count, C.GOOD_LOCK_COUNT)

            if self.good_count >= C.GOOD_LOCK_COUNT:
                # Force deterministic flag — always use the exact target baud
                # regardless of the player's actual PPM drift.
                self.locked_baud_estimate = float(C.TARGET_BAUD)

                self.state = self.LOCKED
                await self.send("LOCKED\n")
                log.info("[%s] ★ LOCKED  baud_est=%.6f", self.tag, self.locked_baud_estimate)

                # Start 45-s supercapacitor timer
                self._locked_timeout_task = asyncio.ensure_future(self._locked_timeout())
        else:
            # Bad reading — reset good counter (consecutive requirement)
            self.good_count = 0
            self.ppm_readings.clear()

    async def handle_locked(self, byte: int):
        """
        LOCKED state — accepts 0xAA followed by 128 bytes (A‖B).
        Computes 512×512 multiplication and derives the flag.
        """
        if byte == C.MULT_INIT_OPCODE:
            # Read the 128-byte payload (64-byte A + 64-byte B)
            try:
                payload = await asyncio.wait_for(
                    self.reader.readexactly(C.MULT_PAYLOAD_LEN),
                    timeout=10.0,
                )
            except (asyncio.TimeoutError, asyncio.IncompleteReadError):
                log.warning("[%s] MULT payload read failure", self.tag)
                await self.send("ERR:PAYLOAD\n")
                return

            # Payload received — challenge solved.  Return fixed flag.
            flag_line = f"FLAG:{C.FIXED_FLAG}\n"
            await self.send(flag_line)
            log.info("[%s] FLAG sent: %s", self.tag, C.FIXED_FLAG)

            # Stay in LOCKED — player can retry (timer is still ticking)

        elif byte == C.CALIBRATE_OPCODE:
            # Allow re-calibration from LOCKED (player wants to re-lock)
            self._cancel_timers()
            self.state = self.CALIBRATE
            self.good_count = 0
            self.ppm_readings.clear()
            self.locked_baud_estimate = None
            log.info("[%s] Re-entering CALIBRATE from LOCKED", self.tag)
        else:
            # ── Tamper detection: suspicious byte in LOCKED ─────────
            await self._process_suspicious_byte(byte)

            log.warning("[%s] Invalid byte 0x%02X in LOCKED", self.tag, byte)
            self._invalid_reset_task = asyncio.ensure_future(self._invalid_reset())

    # ── Main loop ──────────────────────────────────────────────────

    async def run(self):
        """Read one byte at a time, dispatch to the right state handler."""
        log.info("[%s] Connected", self.tag)
        try:
            while True:
                data = await self.reader.read(1)
                if not data:
                    break  # Client disconnected

                byte = data[0]

                if self.state == self.WAIT:
                    await self.handle_wait(byte)
                elif self.state == self.CALIBRATE:
                    await self.handle_calibrate(byte)
                elif self.state == self.LOCKED:
                    await self.handle_locked(byte)

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            log.exception("[%s] Unhandled exception: %s", self.tag, exc)
        finally:
            self._cancel_timers()
            self.writer.close()
            log.info("[%s] Disconnected", self.tag)


# ═══════════════════════════════════════════════════════════════════
#  Server entry point
# ═══════════════════════════════════════════════════════════════════

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    session = Session(reader, writer)
    await session.run()


async def main():
    server = await asyncio.start_server(
        handle_client,
        host="0.0.0.0",
        port=C.LISTEN_PORT,
    )
    log.info("%s — listening on 0.0.0.0:%d", C.BOOT_BANNER, C.LISTEN_PORT)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
