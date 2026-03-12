"""Async TCP server entrypoint for RTUN v1.0."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from .logic import RTUNConfig, RTUNHandler
from .packet import CRC_LEN, HEADER_LEN, MAX_PAYLOAD_LEN, PacketHeader


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "3001"))
FLAG = os.environ.get("FLAG", "apoorvctf{test_flag_replace_me}")
CLIENT_IDLE_TIMEOUT_SEC = float(os.environ.get("CLIENT_IDLE_TIMEOUT_SEC", "60"))
MAX_CONNECTION_LIFETIME_SEC = float(os.environ.get("MAX_CONNECTION_LIFETIME_SEC", "600"))
TCP_BACKLOG = int(os.environ.get("TCP_BACKLOG", "1024"))
MAX_BUFFER_DRAIN_PER_TURN = int(os.environ.get("MAX_BUFFER_DRAIN_PER_TURN", "8192"))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rtun.tcp")


class StreamReadError(Exception):
    """Raised when a connection sends a malformed or incomplete packet."""

    def __init__(self, response: bytes, close_connection: bool = True) -> None:
        super().__init__(response.decode("ascii", errors="replace"))
        self.response = response
        self.close_connection = close_connection


def _next_timeout(deadline: float) -> float:
    """
    Timeout for the next blocking operation:
    bounded by both idle timeout and per-connection lifetime deadline.
    """
    remaining = deadline - asyncio.get_running_loop().time()
    if remaining <= 0:
        raise asyncio.TimeoutError
    return min(CLIENT_IDLE_TIMEOUT_SEC, remaining)


async def _read_header(reader: asyncio.StreamReader, timeout: float) -> Optional[bytes]:
    """
    Read fixed-size RTUN header.
    Returns None for clean disconnect before packet start.
    """
    try:
        return await asyncio.wait_for(
            reader.readexactly(HEADER_LEN), timeout=timeout
        )
    except asyncio.TimeoutError:
        raise
    except asyncio.IncompleteReadError as exc:
        if not exc.partial:
            return None
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")


async def _read_tail(reader: asyncio.StreamReader, n: int, timeout: float) -> bytes:
    """Read payload+CRC bytes for one packet."""
    try:
        return await asyncio.wait_for(
            reader.readexactly(n), timeout=timeout
        )
    except asyncio.TimeoutError:
        raise
    except asyncio.IncompleteReadError:
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")


async def _read_packet(reader: asyncio.StreamReader, deadline: float) -> Optional[bytes]:
    """
    Read exactly one RTUN packet from stream.
    Returns None on clean disconnect before next packet.
    """
    header_raw = await _read_header(reader, _next_timeout(deadline))
    if header_raw is None:
        return None

    try:
        header = PacketHeader.unpack_from(header_raw)
    except ValueError:
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")

    # Bound packet body before reading tail to avoid oversized reads.
    if header.payload_len > MAX_PAYLOAD_LEN:
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")

    tail = await _read_tail(
        reader, header.payload_len + CRC_LEN, _next_timeout(deadline)
    )
    return header_raw + tail


async def _drain_writer(writer: asyncio.StreamWriter, timeout: float) -> None:
    """Bound response flush so slow readers cannot pin handler tasks forever."""
    await asyncio.wait_for(writer.drain(), timeout=timeout)


async def _send_response(
    writer: asyncio.StreamWriter, response: bytes, timeout: float
) -> bool:
    """Write and flush one server response. Returns False on socket failure/timeout."""
    writer.write(response)
    try:
        await _drain_writer(writer, timeout)
    except (asyncio.TimeoutError, ConnectionError):
        return False
    return True


def _buffered_len(reader: asyncio.StreamReader) -> int:
    """Best-effort unread-byte count currently staged in StreamReader buffer."""
    return len(getattr(reader, "_buffer", b""))


async def _discard_buffered_bytes(
    reader: asyncio.StreamReader, n: int, timeout: float
) -> bool:
    """
    Discard exactly n bytes that are already staged in StreamReader buffer.
    Returns False if the stream cannot provide the expected bytes.
    """
    if n <= 0:
        return True
    try:
        await asyncio.wait_for(reader.readexactly(n), timeout=timeout)
    except (asyncio.TimeoutError, asyncio.IncompleteReadError):
        return False
    return True


async def _handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, rtun: RTUNHandler
) -> None:
    deadline = asyncio.get_running_loop().time() + MAX_CONNECTION_LIFETIME_SEC
    while True:
        try:
            raw = await _read_packet(reader, deadline)
            if raw is None:
                break
        except asyncio.TimeoutError:
            break
        except StreamReadError as exc:
            try:
                timeout = _next_timeout(deadline)
            except asyncio.TimeoutError:
                break
            await _send_response(writer, exc.response, timeout)
            if exc.close_connection:
                break
            continue
        except (ConnectionError, OSError):
            break

        queued_before_response = _buffered_len(reader)
        if queued_before_response > MAX_BUFFER_DRAIN_PER_TURN:
            try:
                timeout = _next_timeout(deadline)
            except asyncio.TimeoutError:
                break
            await _send_response(writer, b"RTUN/1.0 ERR_LEN", timeout)
            break

        response, should_close = rtun.handle_packet(raw)
        try:
            timeout = _next_timeout(deadline)
        except asyncio.TimeoutError:
            break
        if not await _send_response(writer, response, timeout):
            break

        if queued_before_response:
            try:
                timeout = _next_timeout(deadline)
            except asyncio.TimeoutError:
                break
            if not await _discard_buffered_bytes(
                reader, queued_before_response, timeout
            ):
                break
        if queued_before_response:
            log.warning(
                "Discarded %d queued bytes before reading next command",
                queued_before_response,
            )

        if should_close:
            break

    writer.close()
    try:
        await writer.wait_closed()
    except ConnectionError:
        pass


async def _serve() -> None:
    cfg = RTUNConfig(flag_value=FLAG)

    async def on_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        # Keep per-connection handler instances isolated from each other.
        rtun = RTUNHandler(cfg)
        await _handle_client(reader, writer, rtun)

    server = await asyncio.start_server(
        on_client,
        HOST,
        PORT,
        backlog=TCP_BACKLOG,
    )
    async with server:
        log.info("=" * 55)
        log.info("  RTUN/1.0 Router — Async TCP Server")
        log.info("  Listening on TCP %s:%d", HOST, PORT)
        log.info("  Nodes : 1 (yours)  2 (busy)  3 (restricted)")
        log.info("  Idle timeout per client: %.0fs", CLIENT_IDLE_TIMEOUT_SEC)
        log.info("  Max connection lifetime: %.0fs", MAX_CONNECTION_LIFETIME_SEC)
        log.info("  Flag  : %s", "*" * len(FLAG))
        log.info("=" * 55)
        await server.serve_forever()


def main() -> None:
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        log.info("Shutting down.")


if __name__ == "__main__":
    main()
