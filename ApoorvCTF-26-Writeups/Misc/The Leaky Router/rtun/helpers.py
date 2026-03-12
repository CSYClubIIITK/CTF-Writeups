"""Small shared helpers used by RTUN logic."""

from __future__ import annotations

import zlib


def crc32_u32(data: bytes) -> int:
    """Return zlib CRC32 as unsigned uint32."""
    return zlib.crc32(data) & 0xFFFFFFFF  # zlib.crc32 returns signed int, but we want unsigned for easier comparisons and packing.


def safe_ascii(data: bytes) -> bytes:
    """Convert arbitrary bytes to safe printable ASCII bytes."""
    return data.decode("ascii", errors="replace").encode("ascii", errors="replace")
