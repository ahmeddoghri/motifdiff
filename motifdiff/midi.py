from __future__ import annotations

from pathlib import Path

REST = -1


def _varlen(value: int) -> bytes:
    buffer = value & 0x7F
    value >>= 7
    out = []
    while value:
        out.append((buffer | 0x80) & 0xFF)
        buffer = value & 0x7F
        value >>= 7
    out.append(buffer)
    return bytes(reversed(out))


def write_midi(sequence: list[int], path: str | Path, tempo_bpm: int = 108) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ticks = 120
    tempo = int(60_000_000 / tempo_bpm)
    track = bytearray()
    track.extend(b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big"))
    pending_delta = 0
    for pitch in sequence:
        if pitch == REST:
            pending_delta += ticks
            continue
        track.extend(_varlen(pending_delta))
        track.extend(bytes([0x90, pitch, 84]))
        track.extend(_varlen(ticks))
        track.extend(bytes([0x80, pitch, 0]))
        pending_delta = 0
    track.extend(_varlen(pending_delta))
    track.extend(b"\xff\x2f\x00")
    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") + (1).to_bytes(2, "big") + (480).to_bytes(2, "big")
    chunk = b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    path.write_bytes(header + chunk)
    return path
