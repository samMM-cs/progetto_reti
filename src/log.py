from datetime import datetime
from json import JSONDecodeError, load, dump
from base64 import standard_b64encode
from io import IOBase


def log_packet(handle: IOBase, receiver_address: tuple[str, int], sender_address: tuple[str, int], payload: bytes):
    to_log: dict[str, str | int] = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "receiver_address": f"{receiver_address[0]}:{receiver_address[1]}",
        "sender_address": f"{sender_address[0]}:{sender_address[1]}",
        "payload_length": len(payload),
        "payload": standard_b64encode(payload).decode()
    }
    handle.seek(0)
    try:
        l: list[dict[str, str | int]] = load(handle)
    except JSONDecodeError as e:  # file corrotto o vuoto
        l = []
        print(e)
    print(type(l))
    l.append(to_log)
    handle.seek(0)
    handle.truncate()
    dump(l, handle)
