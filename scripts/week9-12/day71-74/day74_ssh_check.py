import logging
from getpass import getpass

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from day72_check import load_rules, check_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

SEV = {"high": "HIGH", "medium": "MED ", "low": "LOW "}


def load_devices(path="devices.yaml"):
    with open(path, encoding="utf-8") as f:
        devices = yaml.safe_load(f)
    if not devices:
        raise ValueError(f"设备清单为空: {path}")
    return devices


def fetch_config(dev, password):
    conn = ConnectHandler(
        device_type=dev.get("device_type", "huawei"),
        host=dev["host"],
        username=dev["username"],
        password=password,
        timeout=15,
    )
    try:
        return conn.send_command(
            "display current-configuration",
            read_timeout=180,
        )
    finally:
        conn.disconnect()


def report_one(dev, results):
    total = len(results)
    n_pass = sum(1 for r in results if r["pass"])
    n_fail = total - n_pass
    logging.info(
        "%s (%s)：%d 项检查，通过 %d，违规 %d",
        dev["name"], dev["host"], total, n_pass, n_fail,
    )
    for r in results:
        if r["pass"]:
            continue
        logging.warning(
            "  [%s] %s %s —— 违规！建议：%s",
            SEV.get(r["severity"], r["severity"]),
            r["id"], r["name"], r["advice"],
        )


def main():
    rules = load_rules("rules.yaml")
    password = getpass("设备统一密码: ")
    for dev in load_devices():
        name = dev["name"]
        try:
            cfg = fetch_config(dev, password)
        except NetmikoTimeoutException:
            logging.error("%s 连接超时：网络不通或设备没开 SSH", name)
            continue
        except NetmikoAuthenticationException:
            logging.error("%s 认证失败：用户名/密码或 aaa 配置问题", name)
            continue
        except Exception as e:
            logging.error("%s 未预期错误：%s", name, e)
            continue
        report_one(dev, check_config(cfg, rules))


if __name__ == "__main__":
    main()