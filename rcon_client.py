"""Small Source RCON client used by PalAdminPanel.

Palworld uses the Source RCON wire protocol. Keeping the protocol client here
avoids depending on a command-line utility or a package with subtly different
command argument handling.
"""

from __future__ import annotations

import socket
import struct
from dataclasses import dataclass


class RconError(RuntimeError):
    """Base exception for RCON failures."""


class RconAuthenticationError(RconError):
    """Raised when the server rejects the RCON password."""


class RconProtocolError(RconError):
    """Raised when a malformed RCON packet is received."""


@dataclass(frozen=True)
class RconPacket:
    request_id: int
    packet_type: int
    body: str


class SourceRconClient:
    SERVERDATA_RESPONSE_VALUE = 0
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    MAX_PACKET_SIZE = 10 * 1024 * 1024

    def __init__(self, host: str, port: int, password: str, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout

    @staticmethod
    def _encode_packet(request_id: int, packet_type: int, body: str) -> bytes:
        payload = struct.pack("<ii", request_id, packet_type)
        payload += body.encode("utf-8") + b"\x00\x00"
        return struct.pack("<i", len(payload)) + payload

    @staticmethod
    def _read_exact(sock: socket.socket, length: int) -> bytes:
        chunks: list[bytes] = []
        remaining = length
        while remaining:
            chunk = sock.recv(remaining)
            if not chunk:
                raise RconProtocolError("RCON connection closed unexpectedly")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    @classmethod
    def _read_packet(cls, sock: socket.socket) -> RconPacket:
        raw_size = cls._read_exact(sock, 4)
        (size,) = struct.unpack("<i", raw_size)
        if size < 10 or size > cls.MAX_PACKET_SIZE:
            raise RconProtocolError(f"Invalid RCON packet size: {size}")
        payload = cls._read_exact(sock, size)
        request_id, packet_type = struct.unpack("<ii", payload[:8])
        if payload[-2:] != b"\x00\x00":
            raise RconProtocolError("RCON packet is missing terminators")
        body = payload[8:-2].decode("utf-8", errors="replace")
        return RconPacket(request_id, packet_type, body)

    def run(self, command: str, allow_no_response: bool = False) -> str:
        if not command or "\x00" in command:
            raise ValueError("RCON command must be non-empty and cannot contain NUL")

        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                sock.settimeout(self.timeout)
                sock.sendall(self._encode_packet(1, self.SERVERDATA_AUTH, self.password))

                authenticated = False
                for _ in range(3):
                    packet = self._read_packet(sock)
                    if packet.request_id == -1:
                        raise RconAuthenticationError("RCON password was rejected")
                    if packet.packet_type == self.SERVERDATA_AUTH_RESPONSE and packet.request_id == 1:
                        authenticated = True
                        break
                if not authenticated:
                    raise RconProtocolError("No RCON authentication response received")

                sock.sendall(self._encode_packet(2, self.SERVERDATA_EXECCOMMAND, command))
                try:
                    first = self._read_packet(sock)
                except socket.timeout:
                    if allow_no_response:
                        return ""
                    raise
                # PalDefender 1.8.3 replies with request id 0 even when the
                # request used another positive id. Vanilla Palworld normally
                # echoes id 2, so accept both non-negative forms.
                if first.request_id < 0:
                    raise RconProtocolError("RCON command was rejected")

                parts = [first.body]
                sock.settimeout(0.12)
                while True:
                    try:
                        packet = self._read_packet(sock)
                    except socket.timeout:
                        break
                    if packet.request_id not in {first.request_id, 2}:
                        break
                    parts.append(packet.body)
                return "".join(parts).strip()
        except RconError:
            raise
        except (TimeoutError, socket.timeout) as exc:
            raise RconError("RCON connection timed out") from exc
        except OSError as exc:
            raise RconError(f"Cannot connect to RCON at {self.host}:{self.port}") from exc
