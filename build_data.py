from datetime import datetime
from json import load, dump
from src.net_test import lengths, intervals, directory


def coalesce_logs():
  proto = "udp"
  hosts = ["H4", "H5", "H6"]
  full_log = dict()
  for host in hosts:
    full_log[host] = dict()
    for interval in intervals:
      full_log[host][interval] = dict()
      for length in lengths:
        full_log[host][interval][length] = dict()
        log_file = f"{directory}%s_log_{host}_{interval}_{length}_{proto}.json"
        with open(log_file % "server") as f:
          tmp = load(f)
          useful = [{"timestamp": datetime.fromisoformat(rec["timestamp"]),
                    "payload_length": rec["payload_length"]} for rec in tmp]
          times = [rec["timestamp"] for rec in useful]
          full_log[host][interval][length]["server"] = {"sent": len(useful),
                                                        "data": sum(rec["payload_length"] for rec in useful),
                                                        "time": (max(times) - min(times)).total_seconds()}
        with open(log_file % "client") as f:
          full_log[host][interval][length]["client"] = load(f)
  return full_log


def dump_useful_logs(full_log, file_name):
  with open(file_name, "w+") as f:
    dump(full_log, f)
