import json
import sys
from datetime import date
from getpass import getpass
from pathlib import Path

from jinja2 import Template
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command

HERE = Path(__file__).resolve().parent                 # day78-81
WEEK = HERE.parent
ENGINE_DIR = WEEK / "day71-74"
NORNIR_DIR = WEEK / "day75-77"

sys.path.insert(0, str(ENGINE_DIR))
from day72_check import load_rules, check_config
from day74_ssh_check import report_one


def check_host(task, rules):
    cmd = task.run(
        task=netmiko_send_command,
        command_string="display current-configuration",
        read_timeout=180,
    )
    return check_config(cmd.result, rules)


def main():
    rules = load_rules(str(ENGINE_DIR / "rules.yaml"))
    nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(NORNIR_DIR / "host.yaml"),
                "group_file": str(NORNIR_DIR / "group.yaml"),
                "defaults_file": str(NORNIR_DIR / "defaults.yaml"),
            },
        },
        runner={"plugin": "threaded", "options": {"num_workers": 5}},
    )
    pw = getpass("设备统一密码: ")
    for host in nr.inventory.hosts.values():
        host.password = pw

    all_results = []
    agg = nr.run(task=check_host, rules=rules)
    for name, multi in agg.items():
        host = nr.inventory.hosts[name]
        rec = {
            "name": name,
            "host": str(host.hostname),
            "passed": 0,
            "total": 0,
            "results": [],
        }
        if multi.failed:
            print(f"{name} 采集失败: {multi.exception}")
            all_results.append(rec)
            continue
        results = multi.result
        rec["results"] = results
        rec["total"] = len(results)
        rec["passed"] = sum(1 for r in results if r["pass"])
        report_one({"name": name, "host": rec["host"]}, results)
        all_results.append(rec)

    report = {"scan_time": str(date.today()), "devices": all_results}

    json_path = HERE / "compliance_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(HERE / "report.j2", encoding="utf-8") as f:
        html = Template(f.read()).render(**report)
    html_path = HERE / "合规检查报告.html"
    html_path.write_text(html, encoding="utf-8")
    print("已写入", json_path)
    print("报告已生成", html_path)


if __name__ == "__main__":
    main()