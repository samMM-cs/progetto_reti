import datetime
from mininet.log import info


def log_packet(handle, receiver_address: tuple[str, int], sender_address: tuple[str, int], payload: bytes):
    to_log = f"{datetime.datetime.now().astimezone().isoformat()}, {receiver_address[0]}:{receiver_address[1]}, {sender_address[0]}:{sender_address[1]}, {len(payload)}, {payload}\n"
    handle.write(to_log)


def exe_and_log(exe, cmd):
    res = exe.cmd(cmd)
    info(exe.name + ': ' + cmd + '\n' + str(res)+'\n\n')
