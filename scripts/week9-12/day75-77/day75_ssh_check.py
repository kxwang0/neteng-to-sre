from getpass import getpass
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command

import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent          # .../day75-77
ENGINE_DIR = HERE.parent / "day71-74"           # .../day71-74
sys.path.insert(0, str(ENGINE_DIR))
from day72_check import load_rules, check_config
from day74_ssh_check import report_one

def check_host(task, rules):
    cmd = task.run(
        task=netmiko_send_command,
        command_string="display current-configuration",
        read_timeout=180,
    )
    cfg = cmd.result
    results = check_config(cfg, rules)
    return results

def main():
    rules = load_rules("rules.yaml")
    nr = InitNornir(config_file="config.yaml")
    pw = getpass("设备统一密码: ")
    for host in nr.inventory.hosts.values():
        host.password = pw

    agg = nr.run(task=check_host, rules=rules)
    for name, multi in agg.items():
        host = nr.inventory.hosts[name]
        if multi.failed:
            print(f"{name} 采集失败: {multi.exception}")
            continue
        results = multi.result
        report_one(
            {"name": name, "host": str(host.hostname)},
            results,
        )

if __name__ == "__main__":
    main()