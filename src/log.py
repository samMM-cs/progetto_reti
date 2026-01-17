from datetime import datetime
from json import dump
from base64 import standard_b64encode
from io import IOBase


def build_json_entry(receiver_address: tuple[str, int], sender_address: tuple[str, int], payload: bytes) -> dict[str, str | int]:
    return {
        "timestamp": datetime.now().astimezone().isoformat(),
        "receiver_address": f"{receiver_address[0]}:{receiver_address[1]}",
        "sender_address": f"{sender_address[0]}:{sender_address[1]}",
        "payload_length": len(payload),
        "payload": standard_b64encode(payload).decode()
    }


def dump_to_file(handle: IOBase, log):
    handle.seek(0)
    handle.truncate()
    dump(log, handle)
