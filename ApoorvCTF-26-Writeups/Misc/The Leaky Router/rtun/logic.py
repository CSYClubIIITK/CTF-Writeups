"""RTUN protocol validation and routing logic."""

from __future__ import annotations

from dataclasses import dataclass
import struct

from .helpers import crc32_u32, safe_ascii
from .packet import (
    CRC_LEN,
    HEADER_LEN,
    MAX_PAYLOAD_LEN,
    MIN_PACKET_LEN,
    Packet,
    PacketHeader,
    RTUNProto,
    RTUNTunnel,
    RTUNVersion,
)


@dataclass(slots=True)
class RTUNConfig:
    flag_value: str


class ParseError(Exception):
    """Packet validation error with an already-formatted protocol response."""

    def __init__(self, response: bytes) -> None:
        super().__init__(response.decode("ascii", errors="replace"))
        self.response = response


def ok(msg: bytes) -> bytes:
    return b"RTUN/1.0 OK " + msg


def err(msg: bytes) -> bytes:
    return b"RTUN/1.0 " + msg


class RTUNHandler:
    """Validates RTUN packets and returns protocol responses."""

    def __init__(self, cfg: RTUNConfig) -> None:
        self.cfg = cfg

    def parse_packet(self, raw: bytes) -> Packet:
        """
        Parse and validate a full RTUN packet.

        Check order follows the challenge docs:
          1) VERSION
          2) minimum packet length
          3) CRC32
          4) PAYLOAD_LEN + payload bounds
          5) INNER_PROTO validity
        """
        # 1) VERSION first byte check
        if len(raw) < 1 or raw[0] != RTUNVersion.V1:
            raise ParseError(err(b"ERR_VERSION"))

        # 2) basic packet length floor
        if len(raw) < MIN_PACKET_LEN:
            raise ParseError(err(b"ERR_LEN"))

        # 3) checksum validation over bytes before trailing CRC32
        recv_crc = struct.unpack(">I", raw[-CRC_LEN:])[0]
        calc_crc = crc32_u32(raw[:-CRC_LEN])
        if recv_crc != calc_crc:
            raise ParseError(err(b"ERR_CHECKSUM"))

        # Unpack header and extract payload
        header = PacketHeader.unpack_from(raw[:HEADER_LEN])
        payload = raw[HEADER_LEN:-CRC_LEN]
        expected_len = HEADER_LEN + header.payload_len + CRC_LEN

        # Enforce strict upper/lower packet bound from PAYLOAD_LEN declaration.
        if len(raw) != expected_len:
            raise ParseError(err(b"ERR_LEN"))

        # 4) payload size checks
        if header.payload_len != len(payload):
            raise ParseError(err(b"ERR_LEN"))
        if header.payload_len > MAX_PAYLOAD_LEN:
            raise ParseError(err(b"ERR_LEN"))

        # 5) inner proto checks
        if header.inner_proto not in RTUNProto.VALID:
            raise ParseError(
                err(
                    b"ERR_PROTO: unknown protocol 0x"
                    + f"{header.inner_proto:02x}".encode()
                )
            )

        return Packet(header=header, payload=payload, crc32=recv_crc)

    def route_packet(self, pkt: Packet) -> bytes:
        """Apply tunnel routing, auth gates, and proto dispatch."""
        tunnel_id = pkt.header.tunnel_id

        if tunnel_id not in RTUNTunnel.VALID:
            return err(b"ERR_TUNNEL: unknown tunnel 0x" + f"{tunnel_id:08x}".encode())

        if tunnel_id == RTUNTunnel.NODE1:
            return self._dispatch(pkt, node=1, is_flag_node=False)

        if tunnel_id == RTUNTunnel.NODE2:
            if not pkt.skip_auth:
                return err(b"ERR_AUTH: session token mismatch")
            return self._dispatch(pkt, node=2, is_flag_node=False)

        # Node 3
        if not pkt.skip_auth:
            return err(b"ERR_AUTH: Node 3 only accepts packets from Node 2")
        return self._dispatch(pkt, node=3, is_flag_node=True)

    def handle_packet(self, raw: bytes) -> tuple[bytes, bool]:
        """
        Process one packet and return:
          - protocol response bytes
          - whether TCP connection should close after sending this response
        """
        try:
            pkt = self.parse_packet(raw)
            response = self.route_packet(pkt)
        except ParseError as exc:
            return exc.response, False
        except Exception:
            return err(b"ERR_INTERNAL"), False

        close_after_send = response.startswith(b"RTUN/1.0 OK FLAG=")
        return response, close_after_send

    def _dispatch(self, pkt: Packet, node: int, is_flag_node: bool) -> bytes:
        proto = pkt.header.inner_proto

        if proto == RTUNProto.PLAINTEXT:
            return self._handle_plaintext(pkt.payload, node)
        if proto == RTUNProto.COMMAND:
            return self._handle_command(pkt.payload, node)
        if proto == RTUNProto.FLAG_REQ:
            return self._handle_flag_req(pkt.payload, is_flag_node)
        if proto == RTUNProto.ECHO:
            return self._handle_echo(pkt.payload)

        # Should not happen because parse_packet validates proto.
        return err(
            b"ERR_PROTO: unknown protocol 0x"
            + f"{pkt.header.inner_proto:02x}".encode()
        )

    def _handle_plaintext(self, payload: bytes, node: int) -> bytes:
        if not payload:
            return ok(b"hello Node" + str(node).encode() + b", no message provided")
        return ok(
            b"hello Node" + str(node).encode() + b", received: " + safe_ascii(payload)
        )

    def _handle_command(self, payload: bytes, node: int) -> bytes:
        if payload.strip().upper() != b"STATUS":
            return err(b"ERR_PROTO: COMMAND requires payload STATUS")

        return (
            b"RTUN/1.0 STATUS:\n"
            b"  Node 1 - ASSIGNED TO YOU\n"
            b"  Node 2 - BUSY (active session)\n"
            b"  Node 3 - RESTRICTED"
        )

    def _handle_flag_req(self, payload: bytes, is_flag_node: bool) -> bytes:
        if not is_flag_node:
            return err(b"FLAG_REQ acknowledged, but you are not Node2")

        if payload != b"GIVE_FLAG":
            return err(b"ERR_PROTO: FLAG_REQ requires payload GIVE_FLAG")

        return b"RTUN/1.0 OK FLAG=" + self.cfg.flag_value.encode()

    def _handle_echo(self, payload: bytes) -> bytes:
        if not payload:
            return err(b"ERR_PROTO: ECHO requires a non-empty payload")
        return ok(b"ECHO " + payload[:256])
