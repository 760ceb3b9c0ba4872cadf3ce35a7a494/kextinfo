import dataclasses
import subprocess
import uuid
import io


_OPEN_CHARS = {b"<"[0], b"("[0]}
_CLOSE_CHARS = {b">"[0], b")"[0]}


def _special_split(string: bytes) -> list[str]:
    result = []
    buffer = io.BytesIO(bytes(0xFF))
    buffer.seek(0)
    depth = 0

    for index in range(len(string) + 1):
        char = 0x00 if index == len(string) else string[index]
        if char in _OPEN_CHARS:
            depth += 1
        elif char in _CLOSE_CHARS:
            depth -= 1

        if char in {0x20, 0x00} and depth == 0:
            buffer.write(b"\n")
            buffer.seek(0)
            data = buffer.readline()[:-1]
            if data:
                result.append(data.decode("utf-8"))
            buffer.seek(0)
        else:
            buffer.write(bytes([char]))
        # print(f"char={bytes([char])} {depth=} {buffer=}")

    return result


@dataclasses.dataclass
class KextStat:
    index: int
    refs: int
    address: int
    size: int
    wired: int
    name: str
    version: str
    uuid: uuid.UUID
    linked_against: tuple[int]


def kext_stat():
    result = subprocess.run(
        args=["/usr/sbin/kextstat"],
        stdout=subprocess.PIPE
    )
    if result.returncode != 0:
        raise ValueError

    lines = result.stdout.split(b"\n")

    split_lines = [_special_split(line) for line in lines if line]
    if len(split_lines[0]) != 9:
        raise ValueError("kextstat format invalid")

    stats = []
    for index in range(len(split_lines) - 1):
        row = split_lines[index + 1]
        stats.append(KextStat(
            index=int(row[0], 10),
            refs=int(row[1], 10),
            address=int(row[2], 16),
            size=int(row[3], 16),
            wired=int(row[4], 16),
            name=row[5],
            version=row[6][1:-1],
            uuid=uuid.UUID(row[7]),
            linked_against=tuple(int(v) for v in row[8][1:-1].split(" ") if v),
        ))
    return stats
