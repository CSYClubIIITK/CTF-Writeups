"""RTUN packet structures and wire-format helpers."""

from __future__ import annotations

from dataclasses import dataclass
import struct


# VERSION(1B) FLAGS(1B) TUNNEL_ID(4B) INNER_PROTO(1B) PAYLOAD_LEN(2B)
HEADER_FORMAT = ">BBIBH"
HEADER_LEN = struct.calcsize(HEADER_FORMAT)  # 9
CRC_LEN = 4
MIN_PACKET_LEN = HEADER_LEN + CRC_LEN        # 13
MAX_PAYLOAD_LEN = 0x01FF                     # 511


class RTUNVersion:
    V1 = 0x01


class RTUNFlags:
    AUTH = 0x01
    CMP = 0x02
    CMR = 0x04
    BYPASS = 0xFF


class RTUNTunnel:
    NODE1 = 0x00000001
    NODE2 = 0x00000002
    NODE3 = 0x00000003
    VALID = {NODE1, NODE2, NODE3}


class RTUNProto:
    PLAINTEXT = 0x01
    COMMAND = 0x02
    FLAG_REQ = 0x03
    ECHO = 0x04
    VALID = {PLAINTEXT, COMMAND, FLAG_REQ, ECHO}


@dataclass(slots=True)
class PacketHeader:
    version: int
    flags: int
    tunnel_id: int
    inner_proto: int
    payload_len: int

    def pack(self) -> bytes:
        return struct.pack(
            HEADER_FORMAT,
            self.version,
            self.flags,
            self.tunnel_id,
            self.inner_proto,
            self.payload_len,
        )

    @classmethod
    def unpack_from(cls, data: bytes) -> "PacketHeader":
        if len(data) < HEADER_LEN:
            raise ValueError("ERR_LEN")
        version, flags, tunnel_id, inner_proto, payload_len = struct.unpack(
            HEADER_FORMAT, data[:HEADER_LEN]
        )
        return cls(version, flags, tunnel_id, inner_proto, payload_len)


@dataclass(slots=True)
class Packet:
    header: PacketHeader
    payload: bytes
    crc32: int

    @property
    def skip_auth(self) -> bool:
        return self.header.flags == RTUNFlags.BYPASS

    def body_bytes(self) -> bytes:
        """Header + payload (CRC excluded)."""
        return self.header.pack() + self.payload

    def wire_bytes(self) -> bytes:
        """Header + payload + CRC32."""
        return self.body_bytes() + struct.pack(">I", self.crc32)
