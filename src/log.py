import datetime


def log(handle, receiver_address: tuple[str, int], sender_address: tuple[str, int], payload: bytes):
    to_log = f"{datetime.datetime.now().astimezone().isoformat()}, {receiver_address[0]}:{receiver_address[1]}, {sender_address[0]}:{sender_address[1]}, {len(payload)}, {payload}\n"
    handle.write(to_log)
