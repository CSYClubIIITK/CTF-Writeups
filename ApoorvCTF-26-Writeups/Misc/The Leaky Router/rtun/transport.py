"""TCP stream helpers for reading RTUN packets."""

from __future__ import annotations

import select
import socket

from .packet import CRC_LEN, HEADER_LEN, PacketHeader


class StreamReadError(Exception):
    """Raised when the stream cannot provide one full RTUN packet."""

    def __init__(self, response: bytes, close_connection: bool = True) -> None:
        super().__init__(response.decode("ascii", errors="replace"))
        self.response = response
        self.close_connection = close_connection


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Read exactly n bytes from a blocking TCP socket."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError("socket closed")
        buf.extend(chunk)
    return bytes(buf)


def read_packet(sock: socket.socket) -> bytes | None:
    """
    Read exactly one RTUN packet from TCP stream.

    Returns:
      - bytes: a complete raw RTUN packet
      - None: clean client disconnect before next packet starts

    Raises:
      - StreamReadError: malformed/incomplete packet boundaries
      - EOFError: connection closed during packet read
      - socket.timeout: timeout while waiting for bytes
    """
    try:
        header_raw = recv_exact(sock, HEADER_LEN)
    except EOFError:
        # Clean disconnect before next packet.
        return None

    try:
        header = PacketHeader.unpack_from(header_raw)
    except ValueError:
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")

    try:
        tail = recv_exact(sock, header.payload_len + CRC_LEN)
    except EOFError:
        raise StreamReadError(b"RTUN/1.0 ERR_LEN")

    return header_raw + tail


def has_queued_input(sock: socket.socket) -> bool:
    """
    Return True if extra unread bytes are already queued in socket buffer.

    The server uses this to enforce strict request/response sequencing:
    one packet in, one response out, then next packet.
    """
    readable, _, _ = select.select([sock], [], [], 0.0)
    if not readable:
        return False

    try:
        peek = sock.recv(1, socket.MSG_PEEK)
    except (BlockingIOError, InterruptedError):
        return False
    return len(peek) > 0
