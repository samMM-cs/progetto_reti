from datetime import datetime
from json import load, dump
from src.net_test import lengths, intervals


def coalesce_logs(directory):
  proto = "tcp"
  hosts = ["H1", "H2", "H3"]
  full_log = dict()
  for host in hosts:
    full_log[host] = dict()
    for interval in intervals:
      full_log[host][interval] = dict()
      for length in lengths:
        if length == 1472:
          length = 1460
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


def coalesce_together_logs(directory):
  full_log = dict()
  for interval in intervals:
    full_log[interval] = dict()
    for length in lengths:
      full_log[interval][length] = dict()
      server_log_file = f"{directory}server_log_together_{interval}_{length}_tcp.json"
      with open(server_log_file) as f:
        tmp = load(f)
        useful = [{"timestamp": datetime.fromisoformat(rec["timestamp"]),
                   "payload_length": rec["payload_length"]} for rec in tmp]
        times = [rec["timestamp"] for rec in useful]
        full_log[interval][length]["server"] = {"sent": len(useful),
                                                "data": sum(rec["payload_length"] for rec in useful),
                                                "time": (max(times) - min(times)).total_seconds()}
      # {"sent": 30, "data": 122880, "time": 30.186044454574585}
      full_log[interval][length]["client"] = {"sent": 0, "data": 0, "time": 0.0}
      for host in ["H1", "H2", "H3"]:
        client_log_file = f"{directory}{host}_log_together_{interval}_{length}_tcp.json"
        with open(client_log_file) as f:
          tmp = load(f)
          full_log[interval][length]["client"]["sent"] += tmp["sent"]
          full_log[interval][length]["client"]["data"] += tmp["data"]
          full_log[interval][length]["client"]["time"] += tmp["time"]


def dump_useful_logs(full_log, file_name):
  with open(file_name, "w+") as f:
    dump(full_log, f)
