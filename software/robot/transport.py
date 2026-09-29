"""Serial transport to the ESP32 -- the line-protocol plumbing in
docs/electronics.md. Kept separate from robot.arm so kinematics and
sequencing can be developed and tested (robot.kinematics's self-test, for
instance) with zero hardware and no pyserial dependency in the import path.

pyserial is only imported inside connect(), lazily, so `import robot.arm`
doesn't fail on a machine that doesn't have it installed yet.
"""

from __future__ import annotations
import time
from . import config


class TransportError(RuntimeError):
    """Raised on a timeout, an ERR reply, or a port-level failure."""


class SerialTransport:
    """One line out, one line back, with retries. Not thread-safe --
    matches the arm: exactly one command in flight at a time."""

    def __init__(self, port: str, baud: int = config.DEFAULT_BAUD,
                 timeout_s: float = config.DEFAULT_TIMEOUT_S, retries: int = 2):
        self.port = port
        self.baud = baud
        self.timeout_s = timeout_s
        self.retries = retries
        self._ser = None

    def connect(self) -> None:
        import serial  # lazy import, see module docstring
        self._ser = serial.Serial(self.port, self.baud, timeout=self.timeout_s)
        # Most boards, including ESP32 dev kits, reset when the serial
        # port opens (DTR/RTS toggling the auto-reset circuit); give the
        # bootloader + setup() time to finish before sending anything.
        time.sleep(2.0)
        self._ser.reset_input_buffer()
        reply = self.send("PING")
        if not reply.startswith("OK"):
            raise TransportError(f"unexpected PING reply: {reply!r}")

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def __enter__(self) -> "SerialTransport":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def send(self, line: str) -> str:
        """Send one command, return the single-line reply. Raises
        TransportError on timeout or an explicit ERR reply."""
        if self._ser is None:
            raise TransportError("not connected -- call connect() first")

        last_exc: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                self._ser.write((line.strip() + "\n").encode("ascii"))
                self._ser.flush()
                reply = self._ser.readline().decode("ascii", errors="replace").strip()
                if not reply:
                    raise TransportError(f"no reply to {line!r} (timeout)")
                if reply.startswith("ERR"):
                    raise TransportError(f"{line!r} -> {reply}")
                return reply
            except TransportError:
                raise
            except Exception as e:  # serial-level failure -- worth a retry
                last_exc = e
                continue
        raise TransportError(f"transport failure sending {line!r}: {last_exc}")


class SimulatedTransport:
    """Drop-in replacement for SerialTransport with no hardware attached.
    Used by robot.arm when constructed with port=None, and by
    software/sequences.py demo routines that should run and print their
    intended moves without an arm present -- useful for reviewing a
    sequence before ever touching real servos."""

    def __init__(self) -> None:
        self._state = {"base": 0.0, "shoulder": 60.0, "elbow": -90.0,
                        "wrist": 0.0, "grip": 50}

    def connect(self) -> None:
        print("[sim] connected (no hardware)")

    def close(self) -> None:
        print("[sim] closed")

    def __enter__(self) -> "SimulatedTransport":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def send(self, line: str) -> str:
        print(f"[sim] -> {line}")
        parts = line.split()
        cmd = parts[0] if parts else ""
        if cmd == "PING":
            return "OK ARM v1"
        if cmd == "J" and len(parts) == 4:
            self._state["base"] = float(parts[1])
            self._state["shoulder"] = float(parts[2])
            self._state["elbow"] = float(parts[3])
            self._state["wrist"] = -(self._state["shoulder"] + self._state["elbow"])
            return "OK"
        if cmd == "G" and len(parts) == 2:
            self._state["grip"] = int(parts[1])
            return "OK"
        if cmd == "STAT":
            s = self._state
            return f"{s['base']:.1f} {s['shoulder']:.1f} {s['elbow']:.1f} {s['wrist']:.1f} {s['grip']}"
        return "OK"
